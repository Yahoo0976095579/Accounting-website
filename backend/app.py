from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, UniqueConstraint # <-- 確保這裡有 UniqueConstraint
import os
from dotenv import load_dotenv
import re
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload # <-- 在這裡新增這行！

# 載入 .env 檔案中的環境變數
load_dotenv()

app = Flask(__name__)
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True
# --- Flask 配置 ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_development_secret_key_please_change_me') # 確保這裡的值在 .env 中設置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
jwt = JWTManager(app)
# 啟用 CORS，允許前端應用程式訪問
# 在開發階段，可以允許所有來源。生產環境中，請限制為你的前端域名。
#CORS(app, supports_credentials=True, origins=["https://accounting-website-j8a3.vercel.app"]) # supports_credentials=True 允許發送 cookie/會話憑證
#, origins=["https://accounting-website-j8a3.vercel.app/"]
# --- 資料庫初始化 ---
CORS(app, supports_credentials=True, origins=re.compile(r"https://accounting-website-.*\.vercel\.app"))

db = SQLAlchemy(app)    



# server/app.py (在 User 模型內部)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    categories = db.relationship('Category', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    created_groups = db.relationship('Group', foreign_keys='Group.created_by_user_id', backref='creator', lazy=True)
    group_memberships = db.relationship('GroupMember', backref='member_user', lazy=True)
    sent_invitations = db.relationship('Invitation', foreign_keys='Invitation.invited_by_user_id', backref='sender', lazy=True)
    received_invitations = db.relationship('Invitation', foreign_keys='Invitation.invited_user_id', backref='receiver', lazy=True)
    recorded_group_transactions = db.relationship('GroupTransaction', foreign_keys='GroupTransaction.created_by_user_id', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    # === 正確修正：User 的 to_dict() 應該包含群組資訊 ===
    def to_dict(self):
        accepted_memberships = [
            m for m in self.group_memberships if m.status == 'accepted'
        ]
        
        groups_data = []
        default_group_id = None 

        if accepted_memberships:
            first_group_membership = accepted_memberships[0]
            default_group_id = first_group_membership.group_id

            for membership in accepted_memberships:
                group = membership.group
                if group:
                    groups_data.append({
                        'id': group.id,
                        'name': group.name,
                        'description': group.description,
                        'your_role': membership.role
                    })

        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'default_group_id': default_group_id,
            'groups': groups_data
        }


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    transactions = db.relationship('Transaction', back_populates='category_obj', lazy=True)
    group_transactions_with_category = db.relationship('GroupTransaction', backref='category', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}', '{self.type}', User_id: {self.user_id})"

    # === 修正：Category 的 to_dict() 應該只返回類別資訊 ===
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'user_id': self.user_id
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category_obj = db.relationship('Category', back_populates='transactions', lazy=True)

    def __repr__(self):
        return f"Transaction('{self.amount}', '{self.type}', '{self.date}', User_id: {self.user_id})"

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category_id': self.category_id,
            'category_name': self.category_obj.name if self.category_obj else None,
            'user_id': self.user_id
        }
# --- 新增資料庫模型定義 (群組相關) ---

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關係定義：
    # group_members: 該群組的所有成員 (通過 GroupMember 中間表)
    group_members = db.relationship('GroupMember', backref='group', lazy=True)
    # group_transactions: 該群組的所有交易
    group_transactions = db.relationship('GroupTransaction', backref='group', lazy=True)
    # creator: 創建該群組的使用者 (backref='created_groups' 已在 User 模型中定義)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by_user_id': self.created_by_user_id,
            'created_by_username': self.creator.username if self.creator else None, # 透過 creator 關係獲取
            'created_at': self.created_at.isoformat()
        }

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member') # 'admin', 'member'
    status = db.Column(db.String(20), nullable=False, default='accepted') # 'pending', 'accepted', 'rejected'
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關係定義：
    # member_user: 這個成員記錄對應的使用者 (backref='group_memberships' 已在 User 模型中定義)

    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='_group_user_uc'),) # 確保一個使用者在一個群組中只能有一條記錄

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'username': self.member_user.username if self.member_user else None, # 透過 member_user 關係獲取
            'role': self.role,
            'status': self.status,
            'joined_at': self.joined_at.isoformat()
        }

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invited_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 被邀請的使用者ID
    status = db.Column(db.String(20), nullable=False, default='pending') # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True) # 邀請有效期

    # 關係定義：
    # group_obj: 邀請所屬的群組
    group_obj = db.relationship('Group', foreign_keys=[group_id], backref='invitations')
    # sender: 發送邀請的使用者 (backref='sent_invitations' 已在 User 模型中定義)
    # receiver: 接收邀請的使用者 (backref='received_invitations' 已在 User 模型中定義)

    __table_args__ = (UniqueConstraint('group_id', 'invited_user_id', name='_group_invited_user_uc'),) # 確保一個使用者在一個群組中只能有一條未處理的邀請

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'group_name': self.group_obj.name if self.group_obj else None,
            'invited_by_user_id': self.invited_by_user_id,
            'invited_by_username': self.sender.username if self.sender else None,
            'invited_user_id': self.invited_user_id,
            'invited_username': self.receiver.username if self.receiver else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class GroupTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False) # 暫時共用個人類別
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 誰記錄的這筆交易
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # 初版暫不處理分帳，可以先不加或設置為 Nullable

    # 關係定義：
    # creator: 記錄這筆交易的使用者 (backref='recorded_group_transactions' 已在 User 模型中定義)
    # category: 交易的類別 (backref='group_transactions_with_category' 將在 Category 模型中定義)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None, # 透過 category 關係獲取
            'created_by_user_id': self.created_by_user_id,
            'created_by_username': self.creator.username if self.creator else None,
            # 'payer_id': self.payer_id # 如果沒有 payer_id 欄位，就不要在這裡顯示
        }


# --- 數據庫初始化 (在應用程式首次請求前創建所有表) ---
# --- 數據庫初始化 (在應用程式首次請求前創建所有表) ---
# 使用一個旗標確保只在首次請求時執行 db.create_all()
# 因為 @app.before_first_request 在 Flask 2.3+ 中已被移除
with app.app_context():
    db.create_all()
# 這裡不再需要 @app.before_first_request 裝飾器
# 而是直接在應用上下文(app context)中執行 db.create_all()
# 這樣確保在 app.run() 之前就創建好表

# Flask-Login 的 login_view 設置

# --- 認證相關 API ---

# ...existing code...
# app.py

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "用戶名已存在"}), 409 # Conflict

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    try:
        db.session.commit() # 提交用戶，以便獲取 new_user.id

        # 為新用戶添加預設類別 (這部分保留，因為個人記帳也需要類別)
        add_default_categories_for_user(new_user.id)

        # ====== 開始刪除或註釋以下程式碼塊：自動創建個人群組 ======
        # default_group_name = f"{new_user.username} 的個人群組"
        # personal_group = Group(name=default_group_name, created_by_user_id=new_user.id)
        # db.session.add(personal_group)
        # db.session.flush()

        # personal_group_member = GroupMember(
        #     group_id=personal_group.id,
        #     user_id=new_user.id,
        #     role='admin',
        #     status='accepted'
        # )
        # db.session.add(personal_group_member)
        # db.session.commit() # 提交群組和成員
        # ====== 結束刪除或註釋程式碼塊 ======

        # 刷新 new_user 對象，確保其 group_memberships 關係被加載
        # 即使沒有群組，這行也應該保留，因為它會載入其他關係
        db.session.refresh(new_user) 
        # 或者更保險的方式是重新查詢帶有 eager loading 的用戶
        # new_user = User.query.options(joinedload(User.group_memberships).joinedload(GroupMember.group)).get(new_user.id)

        access_token = create_access_token(identity=str(new_user.id))
        return jsonify({
            "message": "User registered and logged in successfully",
            "access_token": access_token,
            "user": new_user.to_dict() # 現在 to_dict() 可能會返回空群組列表
        }), 201
    except Exception as e:
        db.session.rollback()
        print("Registration failed:", e)
        return jsonify({"error": "Registration failed: " + str(e)}), 500

# server/app.py 中的 add_default_categories_for_user 函數
def add_default_categories_for_user(user_id):
    """為新使用者添加一些預設類別"""
    default_categories = [
        Category(name='薪資', type='income', user_id=user_id),
        Category(name='兼職', type='income', user_id=user_id),
        Category(name='投資收益', type='income', user_id=user_id), # <-- 示例：新增一個收入類別
        Category(name='禮金', type='income', user_id=user_id),      # <-- 示例：新增另一個收入類別
        Category(name='餐飲', type='expense', user_id=user_id),
        Category(name='交通', type='expense', user_id=user_id),
        Category(name='購物', type='expense', user_id=user_id),
        Category(name='娛樂', type='expense', user_id=user_id),
        Category(name='水電費', type='expense', user_id=user_id),
        Category(name='房租', type='expense', user_id=user_id), # 示例：新增一個支出類別
        Category(name='醫療', type='expense', user_id=user_id), # 示例：新增一個支出類別
    ]
    db.session.add_all(default_categories)
    db.session.commit()
    print(f"Default categories added for user {user_id}")


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).options(
        joinedload(User.group_memberships).joinedload(GroupMember.group)
    ).first() # 使用 joinedload 確保關係被載入

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Logged in successfully",
            "access_token": access_token,
            "user": user.to_dict() # 現在 to_dict() 應該會包含群組資訊
        }), 200
    else:
        return jsonify({"error": "名稱或密碼錯誤"}), 401

@app.route('/api/logout', methods=['GET'])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200
@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_current_user():
    user = User.query.options(
        joinedload(User.group_memberships).joinedload(GroupMember.group)
    ).get(get_jwt_identity()) # 使用 joinedload 確保關係被載入

    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200
# --- 群組管理 API ---

@app.route('/api/groups', methods=['POST'])
@jwt_required()
def create_group():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"error": "群組名稱為必填項"}), 400

    # 創建群組
    new_group = Group(name=name, description=description, created_by_user_id=get_jwt_identity())
    db.session.add(new_group)
    db.session.commit() # 先提交，以便獲取 new_group.id

    # 將創建者自動添加為群組管理員
    group_member = GroupMember(group_id=new_group.id, user_id=get_jwt_identity(), role='admin', status='accepted')
    db.session.add(group_member)
    db.session.commit()

    return jsonify({"message": "群組創建成功", "group": new_group.to_dict()}), 201

@app.route('/api/groups', methods=['GET'])
@jwt_required()
def get_user_groups():
    # 獲取當前使用者所屬的所有群組
    memberships = GroupMember.query.filter_by(user_id=get_jwt_identity(), status='accepted').all()
    groups_data = []
    for membership in memberships:
        group = membership.group # 透過關係獲取 Group 對象
        if group:
            group_dict = group.to_dict()
            group_dict['your_role'] = membership.role # 附加上使用者在該群組的角色
            group_dict['member_count'] = len(group.group_members) # 成員數量
            groups_data.append(group_dict)
    return jsonify(groups_data), 200

@app.route('/api/groups/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group_details(group_id):
    # 確保使用者是群組成員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    group = group_member.group
    group_details = group.to_dict()
    group_details['your_role'] = group_member.role

    members_data = []
    for member in group.group_members:
        members_data.append(member.to_dict())
    group_details['members'] = members_data

    # 這裡可以選擇性地添加群組的總收支等摘要信息
    # group_details['summary'] = {} # TODO: Implement group summary API later

    return jsonify(group_details), 200

@app.route('/api/groups/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    # 檢查使用者是否為群組管理員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), role='admin', status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您無權修改該群組"}), 403 # Forbidden

    group = group_member.group
    data = request.get_json()
    group.name = data.get('name', group.name)
    group.description = data.get('description', group.description)

    try:
        db.session.commit()
        return jsonify({"message": "群組更新成功", "group": group.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "群組更新失敗: " + str(e)}), 500

# app.py (在 delete_group 函數中)

# app.py (在 delete_group 函數中)

@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    # 檢查使用者是否為群組管理員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), role='admin', status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您無權刪除該群組"}), 403 # Forbidden

    group = Group.query.get(group_id) # 直接查詢群組，確保關係是 lazy 加載的
    if not group: # 再次檢查群組是否存在 (雖然前面 GroupMember 檢查過了，但這是更直接的)
        return jsonify({"error": "群組未找到"}), 404

    # === 修正點：只檢查是否有其他活躍成員 ===
    # 獲取活躍成員數量。因為創建者也是成員，如果只有他自己，成員數量就是 1。
    # 所以如果成員數量大於 1，就表示還有其他成員。
    active_member_count = GroupMember.query.filter_by(
        group_id=group_id,
        status='accepted'
    ).count()

    if active_member_count > 1:
        # 如果有其他活躍成員，則不允許刪除
        return jsonify({"error": "群組中仍有其他活躍成員，無法直接刪除。請先移除所有其他成員。"}), 400

    # === 修正點：移除對 GroupTransaction 的檢查 ===
    # 因為需求是如果只有一個成員 (即創建者/管理員) 就可以直接刪除所有，
    # 所以不再檢查交易記錄，而是直接在 try 塊中刪除。

    try:
        # 刪除所有相關的 GroupMember 記錄
        GroupMember.query.filter_by(group_id=group_id).delete(synchronize_session=False) # synchronize_session=False 避免競態條件
        
        # 刪除所有相關的 GroupTransaction 記錄 (即使有，也會在這裡被刪除)
        GroupTransaction.query.filter_by(group_id=group_id).delete(synchronize_session=False) # synchronize_session=False 避免競態條件

        # 如果你還有 Invitation 或其他與 Group 直接相關的表，也需要在這裡刪除
        Invitation.query.filter_by(group_id=group_id).delete(synchronize_session=False) # 刪除相關邀請

        db.session.delete(group) # 最後刪除群組本身
        db.session.commit()
        return jsonify({"message": "群組刪除成功"}), 204
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting group {group_id}: {e}")
        return jsonify({"error": "群組刪除失敗: " + str(e)}), 500

@app.route('/api/groups/<int:group_id>/leave', methods=['POST'])
@jwt_required()
def leave_group(group_id):
    current_user_id = get_jwt_identity()
    # 查找使用者在該群組的成員身份
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=current_user_id, status='accepted').first()
    if not group_member:
        return jsonify({"error": "您不是該群組成員"}), 404

    # === 修正點：完善唯一管理員退出群組的檢查 ===
    if group_member.role == 'admin': # 如果要退出的用戶是管理員
        active_admins_count = GroupMember.query.filter_by(
            group_id=group_id,
            role='admin',
            status='accepted'
        ).count()
        
        # 如果當前用戶是唯一的管理員 (active_admins_count == 1)
        # 且群組中還有其他非管理員成員存在
        if active_admins_count == 1 and GroupMember.query.filter_by(group_id=group_id, status='accepted').count() > 1:
            return jsonify({"error": "您是該群組的唯一管理員，請先將管理權限轉移給其他活躍成員，然後再嘗試退出。"}), 400
        
        # 如果是唯一管理員，但群組中沒有其他成員（只有自己），則允許退出
        # 因為群組會因為沒有成員而自動變成空，且之後可以考慮刪除
        
    # === 結束修正點 ===

    try:
        # 在刪除成員身份之前，需要將該成員記錄的所有群組交易關聯設置為 NULL 或其他預設值
        # 如果 GroupTransaction.created_by_user_id 有外鍵約束 ON DELETE SET NULL 或 ON DELETE CASCADE，則可以省略此處
        # 如果沒有，當成員退出時，其創建的群組交易的 created_by_user_id 就會變成懸空的外鍵。
        # 最簡單的方法是，如果一個成員退出，他創建的交易仍然存在，但 "created_by_user_id" 保持不變，
        # 只是前端在顯示時，如果該用戶已經不是成員，顯示 "已退出成員" 或類似。
        # 這裡不對 GroupTransaction 進行處理，假設歷史數據可以保留其 created_by_user_id

        db.session.delete(group_member)
        db.session.commit()
        return jsonify({"message": "已成功退出群組"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error leaving group {group_id} for user {current_user_id}: {e}")
        return jsonify({"error": "退出群組失敗: " + str(e)}), 500
@app.route('/api/groups/<int:group_id>/members/<int:member_id>/role', methods=['PUT'])
@jwt_required()
def update_group_member_role(group_id, member_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_role = data.get('role')

    if new_role not in ['admin', 'member']:
        return jsonify({"error": "無效的角色。角色必須是 'admin' 或 'member'。"}), 400

    # 1. 檢查操作者 (current_user) 是否為該群組的管理員
    admin_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user_id,
        role='admin',
        status='accepted'
    ).first()
    if not admin_member:
        return jsonify({"error": "群組未找到或您無權修改成員角色"}), 403

    # 2. 獲取要被修改的成員記錄
    member_to_update = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=member_id,
        status='accepted'
    ).first()
    if not member_to_update:
        return jsonify({"error": "成員未找到或不是該群組的活躍成員"}), 404

    # 3. 不允許修改自己的角色
    if member_to_update.user_id == current_user_id:
        return jsonify({"error": "無法透過此介面修改自己的角色。"}), 400

    # 4. 處理管理員降級的情況：不能降級唯一的管理員，如果還有其他活躍成員
    if member_to_update.role == 'admin' and new_role == 'member': # 如果是從 admin 降級到 member
        active_admins_count = GroupMember.query.filter_by(
            group_id=group_id,
            role='admin',
            status='accepted'
        ).count()
        
        # 如果當前被降級的是唯一的管理員 (active_admins_count == 1)
        # 且群組中還有其他非管理員成員 (因為如果只有自己一個管理員，群組可以空或只有自己，那可以降級)
        if active_admins_count == 1 and GroupMember.query.filter_by(group_id=group_id, status='accepted').count() > 1:
            return jsonify({"error": "無法將群組的唯一管理員降級，請先指定其他管理員。"}), 400

    # 5. 更新成員角色
    member_to_update.role = new_role
    try:
        db.session.commit()
        return jsonify({"message": f"成員 {member_to_update.member_user.username} 的角色已更新為 {new_role}"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating member role: {e}")
        return jsonify({"error": "更新成員角色失敗: " + str(e)}), 500

# --- 群組邀請 API ---

@app.route('/api/groups/<int:group_id>/invite', methods=['POST'])
@jwt_required()
def invite_member(group_id):
    # 檢查使用者是否為群組管理員 (這部分不變)
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), role='admin', status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您無權邀請成員"}), 403

    data = request.get_json()
    invited_username = data.get('username')
    if not invited_username:
        return jsonify({"error": "被邀請的使用者名稱為必填項"}), 400

    invited_user = User.query.filter_by(username=invited_username).first()
    if not invited_user:
        return jsonify({"error": "被邀請的使用者不存在"}), 404

    if invited_user.id == get_jwt_identity():
        return jsonify({"error": "不能邀請自己"}), 400

    # === 修正點：重新設計檢查和邀請邏輯 ===

    # 1. 檢查是否已經是群組的活躍成員 (status='accepted')
    existing_active_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=invited_user.id,
        status='accepted'
    ).first()
    if existing_active_member:
        return jsonify({"error": "該使用者已是群組的活躍成員"}), 409

    # 2. 檢查是否存在任何狀態的邀請記錄（包括 pending, accepted, rejected）
    # 因為 UniqueConstraint 是針對 (group_id, invited_user_id) 的，所以只會有一條
    existing_invitation = Invitation.query.filter_by(
        group_id=group_id,
        invited_user_id=invited_user.id
    ).first()

    try:
        if existing_invitation:
            # 如果已有邀請記錄存在
            if existing_invitation.status == 'pending':
                # 如果是待處理狀態，則不允許重複發送
                return jsonify({"error": "已存在對該使用者的待處理邀請"}), 409
            else:
                # 如果是 'rejected' 或 'accepted' (用戶後來被移除的情況)，則更新為 'pending'
                existing_invitation.status = 'pending'
                existing_invitation.created_at = datetime.utcnow() # 更新發送時間
                existing_invitation.invited_by_user_id = get_jwt_identity() # 更新邀請者
                existing_invitation.expires_at = None # 清除過期時間（如果適用）
                db.session.commit()
                return jsonify({"message": f"已成功重新邀請 {invited_username} 加入群組！"}), 200 # 返回 200 表示更新成功
        else:
            # 如果沒有任何邀請記錄，則創建一條新的待處理邀請
            new_invitation = Invitation(
                group_id=group_id,
                invited_by_user_id=get_jwt_identity(),
                invited_user_id=invited_user.id,
                status='pending'
            )
            db.session.add(new_invitation)
            db.session.commit()
            return jsonify({"message": f"已成功向 {invited_username} 發送邀請"}), 201 # 返回 201 表示創建成功
    except Exception as e:
        db.session.rollback()
        # 通常，在上述邏輯正確的情況下，不應該再觸發 UniqueViolation 錯誤
        # 但為了保險，保留通用錯誤捕獲
        print(f"發送邀請失敗 (後端異常): {e}")
        return jsonify({"error": "發送邀請失敗: " + str(e)}), 500

@app.route('/api/invitations', methods=['GET'])
@jwt_required()
def get_user_invitations():
    # 獲取當前使用者收到的所有待處理邀請
    invitations = Invitation.query.filter_by(invited_user_id=get_jwt_identity(), status='pending').all()
    return jsonify([inv.to_dict() for inv in invitations]), 200

@app.route('/api/invitations/<int:invitation_id>/accept', methods=['POST'])
@jwt_required()
def accept_invitation(invitation_id):
    invitation = Invitation.query.filter_by(id=invitation_id, invited_user_id=get_jwt_identity(), status='pending').first()
    if not invitation:
        return jsonify({"error": "邀請未找到或已失效"}), 404

    # 檢查是否已是成員 (以防萬一)
    if GroupMember.query.filter_by(group_id=invitation.group_id, user_id=get_jwt_identity(), status='accepted').first():
        invitation.status = 'rejected' # 如果已是成員，則將邀請狀態設為拒絕
        db.session.commit()
        return jsonify({"error": "您已是該群組成員，邀請已處理"}), 400

    try:
        # 將使用者添加為群組成員
        new_member = GroupMember(group_id=invitation.group_id, user_id=get_jwt_identity(), role='member', status='accepted')
        db.session.add(new_member)
        invitation.status = 'accepted' # 更新邀請狀態
        db.session.commit()
        return jsonify({"message": f"已成功接受邀請，加入群組: {invitation.group_obj.name}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "接受邀請失敗: " + str(e)}), 500

@app.route('/api/invitations/<int:invitation_id>/reject', methods=['POST'])
@jwt_required()
def reject_invitation(invitation_id):
    invitation = Invitation.query.filter_by(id=invitation_id, invited_user_id=get_jwt_identity(), status='pending').first()
    if not invitation:
        return jsonify({"error": "邀請未找到或已失效"}), 404

    try:
        invitation.status = 'rejected' # 更新邀請狀態
        db.session.commit()
        return jsonify({"message": "已成功拒絕邀請"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "拒絕邀請失敗: " + str(e)}), 500

# --- 群組交易 API (簡化版，詳細實現將在後續步驟) ---

#移除成員
# app.py (在群組管理 API 區塊內，例如在 invite_member 附近)

# app.py (在群組管理 API 區塊內)

@app.route('/api/groups/<int:group_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_group_member(group_id, member_id):
    current_user_id = get_jwt_identity()

    # 1. 檢查操作者是否為群組管理員
    admin_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user_id,
        role='admin',
        status='accepted'
    ).first()
    if not admin_member:
        return jsonify({"error": "群組未找到或您無權執行此操作"}), 403 # Forbidden

    # 2. 獲取要被移除的成員記錄
    member_to_remove = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=member_id, # member_id 這裡其實是 user_id
        status='accepted' # 只能移除活躍成員
    ).first()

    if not member_to_remove:
        return jsonify({"error": "成員未找到或不是該群組的活躍成員"}), 404

    # 3. 不允許管理員移除自己 (這個 API 是用於移除他人，自己退出有專門的 leave 接口)
    if member_to_remove.user_id == current_user_id:
        return jsonify({"error": "無法透過此介面移除自己。請使用 '退出群組' 功能。"}), 400

    # 4. 不允許移除群組的唯一管理員 (如果群組還有其他非管理員成員存在)
    if member_to_remove.role == 'admin': # 如果要移除的是管理員
        active_admins_count = GroupMember.query.filter_by(
            group_id=group_id,
            role='admin',
            status='accepted'
        ).count()
        
        # 如果當前管理員是唯一的管理員 (active_admins_count == 1)
        # 且群組中還有其他非管理員成員 (GroupMember.query.filter_by(group_id=group_id, status='accepted').count() > 1)
        # 則不允許移除這個唯一的管理員
        if active_admins_count == 1 and GroupMember.query.filter_by(group_id=group_id, status='accepted').count() > 1:
             return jsonify({"error": "無法移除群組的唯一管理員，請先指定其他管理員。"}), 400

    try:
        db.session.delete(member_to_remove)
        db.session.commit()
        return jsonify({"message": "成員已成功從群組中移除"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error removing group member: {e}")
        return jsonify({"error": "移除成員失敗: " + str(e)}), 500

# 這些 API 只是佔位符，確保其存在且受到保護。
# 細節實現將與個人交易類似，但需考慮 group_id 和權限。

@app.route('/api/groups/<int:group_id>/transactions', methods=['GET'])
@jwt_required()
def get_group_transactions(group_id):
    # 檢查使用者是否為群組成員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    # 篩選參數 (與個人交易類似)
    transaction_type = request.args.get('type') # 'income' or 'expense'
    category_id = request.args.get('category_id', type=int)
    start_date_str = request.args.get('start_date') # YYYY-MM-DD
    end_date_str = request.args.get('end_date')     # YYYY-MM-DD
    search_term = request.args.get('search_term')

    # 分頁參數
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = GroupTransaction.query.filter_by(group_id=group_id) # <-- 關鍵：按 group_id 篩選

    if transaction_type in ['income', 'expense']:
        query = query.filter_by(type=transaction_type)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(GroupTransaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(GroupTransaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
    if search_term:
        query = query.filter(GroupTransaction.description.ilike(f"%{search_term}%"))

    # 排序：最新交易在前
    query = query.order_by(GroupTransaction.date.desc(), GroupTransaction.created_at.desc())

    paginated_transactions = query.paginate(page=page, per_page=per_page, error_out=False)

    transactions_data = [t.to_dict() for t in paginated_transactions.items]

    return jsonify({
        "transactions": transactions_data,
        "total": paginated_transactions.total,
        "pages": paginated_transactions.pages,
        "page": paginated_transactions.page,
        "per_page": paginated_transactions.per_page,
        "has_next": paginated_transactions.has_next,
        "has_prev": paginated_transactions.has_prev
    }), 200

@app.route('/api/groups/<int:group_id>/transactions', methods=['POST'])
@jwt_required()
def add_group_transaction(group_id):
    # 檢查使用者是否為群組成員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    data = request.get_json()
    try:
        amount = float(data.get('amount'))
        transaction_type = data.get('type')
        category_id = data.get('category_id')
        description = data.get('description')
        date_str = data.get('date')

        if not all([amount, transaction_type, category_id, date_str]):
            return jsonify({"error": "缺少必填欄位 (金額, 類型, 類別ID, 日期)"}), 400
        if transaction_type not in ['income', 'expense']:
            return jsonify({"error": "無效的交易類型"}), 400

        # 檢查 category_id 是否存在
        # 注意：這裡的 Category 是共用，不檢查 user_id
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "類別未找到"}), 404

        transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_transaction = GroupTransaction(
            group_id=group_id, # <-- 關鍵：設置 group_id
            amount=amount,
            type=transaction_type,
            description=description,
            date=transaction_date,
            category_id=category_id,
            created_by_user_id=get_jwt_identity() # 記錄誰創建了這筆交易
        )
        db.session.add(new_transaction)
        db.session.commit()
        db.session.refresh(new_transaction) # 刷新以載入關係數據 (如 category_name)
        return jsonify(new_transaction.to_dict()), 201
    except ValueError:
        return jsonify({"error": "金額或日期格式無效"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "新增群組交易失敗: " + str(e)}), 500

@app.route('/api/groups/<int:group_id>/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_group_transaction(group_id, transaction_id):
    # 檢查使用者是否為群組成員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    # 確保交易屬於該群組，且使用者是成員
    transaction = GroupTransaction.query.filter_by(id=transaction_id, group_id=group_id).first()
    if not transaction:
        return jsonify({"error": "交易未找到或不屬於該群組"}), 404
    return jsonify(transaction.to_dict()), 200

@app.route('/api/groups/<int:group_id>/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_group_transaction(group_id, transaction_id):
    # 檢查使用者是否為群組管理員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    # 確保交易屬於該群組
    transaction = GroupTransaction.query.filter_by(id=transaction_id, group_id=group_id).first()
    if not transaction:
        return jsonify({"error": "交易未找到或不屬於該群組"}), 404

    # TODO: 考慮是否只有創建者或管理員才能修改交易？
    # 目前：只要是群組成員就可以修改
    # 考慮：只有管理員能修改其他成員的交易，成員只能修改自己的
    # 簡化：先讓群組成員都可以修改
    # if transaction.created_by_user_id != get_jwt_identity() and group_member.role != 'admin':
    #     return jsonify({"error": "您無權修改此交易"}), 403

    data = request.get_json()
    try:
        if 'amount' in data:
            transaction.amount = float(data.get('amount'))
        if 'type' in data:
            if data.get('type') not in ['income', 'expense']:
                return jsonify({"error": "無效的交易類型"}), 400
            transaction.type = data.get('type')
        if 'description' in data:
            transaction.description = data.get('description')
        if 'date' in data:
            transaction.date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        if 'category_id' in data:
            category_id = data.get('category_id')
            category = Category.query.get(category_id) # 不檢查 user_id
            if not category:
                return jsonify({"error": "類別未找到"}), 404
            transaction.category_id = category_id

        db.session.commit()
        db.session.refresh(transaction) # 刷新以載入關係數據
        return jsonify(transaction.to_dict()), 200
    except ValueError:
        return jsonify({"error": "金額或日期格式無效"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "更新群組交易失敗: " + str(e)}), 500

@app.route('/api/groups/<int:group_id>/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_group_transaction(group_id, transaction_id):
    # 檢查使用者是否為群組成員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    # 確保交易屬於該群組
    transaction = GroupTransaction.query.filter_by(id=transaction_id, group_id=group_id).first()
    if not transaction:
        return jsonify({"error": "交易未找到或不屬於該群組"}), 404

    # TODO: 考慮是否只有創建者或管理員才能刪除交易？
    # 簡化：先讓群組成員都可以刪除
    # if transaction.created_by_user_id != get_jwt_identity() and group_member.role != 'admin':
    #     return jsonify({"error": "您無權刪除此交易"}), 403

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "群組交易刪除成功"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "刪除群組交易失敗: " + str(e)}), 500

# --- 群組統計 API (簡化版，詳細實現將在後續步驟) ---
# 這些 API 也需要填充實際邏輯，類似於個人摘要 API。

@app.route('/api/groups/<int:group_id>/summary', methods=['GET'])
@jwt_required()
def get_group_summary(group_id):
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    total_income = db.session.query(func.sum(GroupTransaction.amount)).filter_by(group_id=group_id, type='income').scalar() or 0
    total_expense = db.session.query(func.sum(GroupTransaction.amount)).filter_by(group_id=group_id, type='expense').scalar() or 0

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    }), 200

@app.route('/api/groups/<int:group_id>/summary/category_breakdown', methods=['GET'])
@jwt_required()
def get_group_category_breakdown(group_id):
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    transaction_type = request.args.get('type') # 'income' or 'expense'
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = db.session.query(
        Category.name,
        Category.type,
        func.sum(GroupTransaction.amount)
    ).join(GroupTransaction).filter(
        GroupTransaction.group_id == group_id, # <-- 關鍵：按 group_id 篩選
    )

    if transaction_type in ['income', 'expense']:
        query = query.filter(GroupTransaction.type == transaction_type)
    if start_date_str:
        try:
            if start_date_str.strip() != "":
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(GroupTransaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date_str:
        try:
            if end_date_str.strip() != "":
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(GroupTransaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
    category_summary = query.group_by(Category.name, Category.type).all()

    summary_by_category = []
    for name, type, total_amount in category_summary:
        summary_by_category.append({
            'category_name': name,
            'type': type,
            'total_amount': total_amount
        })

    return jsonify(summary_by_category), 200

@app.route('/api/groups/<int:group_id>/summary/trend', methods=['GET'])
@jwt_required()
def get_group_trend_data(group_id):
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您不是該群組成員"}), 404

    interval = request.args.get('interval', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = GroupTransaction.query.filter_by(group_id=group_id)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(GroupTransaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(GroupTransaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    # === 修正點：將 func.strftime 改為 func.to_char 並調整格式字串 ===
    if interval == 'day':
        group_by_col = func.to_char(GroupTransaction.date, 'YYYY-MM-DD')
    elif interval == 'week':
        group_by_col = func.to_char(GroupTransaction.date, 'IYYY-IW') # PostgreSQL 的 ISO 週格式
    elif interval == 'month':
        group_by_col = func.to_char(GroupTransaction.date, 'YYYY-MM')
    else:
        return jsonify({"error": "Invalid interval. Must be 'day', 'week', or 'month'."}), 400
    # ================================================================

    income_data = query.with_entities(
        group_by_col.label('period'),
        func.sum(GroupTransaction.amount)
    ).filter(GroupTransaction.type == 'income').group_by('period').order_by('period').all()

    expense_data = query.with_entities(
        group_by_col.label('period'),
        func.sum(GroupTransaction.amount)
    ).filter(GroupTransaction.type == 'expense').group_by('period').order_by('period').all()

    income_map = {item.period: item[1] for item in income_data}
    expense_map = {item.period: item[1] for item in expense_data}

    all_periods = sorted(list(set(income_map.keys()) | set(expense_map.keys())))

    trend_data = []
    for period in all_periods:
        trend_data.append({
            'period': period,
            'income': income_map.get(period, 0),
            'expense': expense_map.get(period, 0),
            'balance': income_map.get(period, 0) - expense_map.get(period, 0)
        })

    return jsonify(trend_data), 200

#下面不動
# --- 類別相關 API (受保護) ---

@app.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = Category.query.filter_by(user_id=get_jwt_identity()).all()
    return jsonify([c.to_dict() for c in categories])

@app.route('/api/categories', methods=['POST'])
@jwt_required()
def add_category():
    data = request.get_json()
    name = data.get('name')
    category_type = data.get('type')

    if not name or not category_type:
        return jsonify({"error": "Name and type are required"}), 400
    if category_type not in ['income', 'expense']:
        return jsonify({"error": "Invalid category type"}), 400

    # 檢查是否已存在相同名稱的類別給當前使用者
    if Category.query.filter_by(user_id=get_jwt_identity(), name=name).first():
        return jsonify({"error": "已存在同名的類別"}), 409

    new_category = Category(name=name, type=category_type, user_id=get_jwt_identity())
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=get_jwt_identity()).first()
    if not category:
        return jsonify({"error": "已存在同名的類別"}), 404

    data = request.get_json()
    name = data.get('name', category.name)
    category_type = data.get('type', category.type)

    if category_type not in ['income', 'expense']:
        return jsonify({"error": "Invalid category type"}), 400

    # 檢查更新後是否會與同使用者下的其他類別名稱重複
    if Category.query.filter(
        Category.user_id == get_jwt_identity(),
        Category.name == name,
        Category.id != category_id
    ).first():
        return jsonify({"error": "Category with this name already exists for this user"}), 409


    category.name = name
    category.type = category_type

    try:
        db.session.commit()
        return jsonify(category.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=get_jwt_identity()).first()
    if not category:
        return jsonify({"error": "Category not found or not owned by user"}), 404

    # 檢查是否有交易記錄關聯到此類別
    if Transaction.query.filter_by(category_id=category_id, user_id=get_jwt_identity()).first():
        return jsonify({"error": "Cannot delete category with associated transactions"}), 400

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- 交易記錄相關 API (受保護，包含篩選和分頁) ---

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    # 篩選參數
    transaction_type = request.args.get('type') # 'income' or 'expense'
    category_id = request.args.get('category_id', type=int)
    start_date_str = request.args.get('start_date') # YYYY-MM-DD
    end_date_str = request.args.get('end_date')     # YYYY-MM-DD
    search_term = request.args.get('search_term') # <-- 新增這行：獲取搜索詞

    # 分頁參數
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Transaction.query.filter_by(user_id=get_jwt_identity())

    if transaction_type in ['income', 'expense']:
        query = query.filter_by(type=transaction_type)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    # <-- 新增這一段：處理搜索詞
    if search_term:
        # 檢查 description 是否包含 search_term (不區分大小寫)
        query = query.filter(Transaction.description.ilike(f"%{search_term}%"))
    # <-- 結束新增部分

    # 排序：最新交易在前
    query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())

    # 執行分頁
    paginated_transactions = query.paginate(page=page, per_page=per_page, error_out=False)

    transactions_data = [t.to_dict() for t in paginated_transactions.items]

    return jsonify({
        "transactions": transactions_data,
        "total": paginated_transactions.total,
        "pages": paginated_transactions.pages,
        "page": paginated_transactions.page,
        "per_page": paginated_transactions.per_page,
        "has_next": paginated_transactions.has_next,
        "has_prev": paginated_transactions.has_prev
    })

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    # 確保使用者只能查看自己的交易記錄
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=get_jwt_identity()).first()
    if not transaction:
        return jsonify({"error": "Transaction not found or not owned by user"}), 404
    return jsonify(transaction.to_dict())

# server/app.py (在 add_transaction 函數內部)
@app.route('/api/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    data = request.get_json()
    try:
        amount = float(data.get('amount'))
        transaction_type = data.get('type')
        category_id = data.get('category_id')
        description = data.get('description')
        date_str = data.get('date') # 期待 YYYY-MM-DD 格式

        if not all([amount, transaction_type, category_id, date_str]):
            return jsonify({"error": "Missing required fields (amount, type, category_id, date)"}), 400
        if transaction_type not in ['income', 'expense']:
            return jsonify({"error": "Invalid transaction type"}), 400

        # 檢查 category_id 是否存在且歸屬於當前使用者
        category = Category.query.filter_by(id=category_id, user_id=get_jwt_identity()).first()
        if not category:
            return jsonify({"error": "Category not found or not owned by user"}), 404

        transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_transaction = Transaction(
            amount=amount,
            type=transaction_type,
            description=description,
            date=transaction_date,
            category_id=category_id,
            user_id=get_jwt_identity() # 設置交易記錄的 user_id
        )
        db.session.add(new_transaction)
        db.session.commit() # 提交到資料庫

        # ===== 新增這行：刷新物件，使其載入所有關聯（包括 category） =====
        db.session.refresh(new_transaction)
        # ================================================================

        return jsonify(new_transaction.to_dict()), 201
    except ValueError:
        return jsonify({"error": "Invalid amount or date format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add transaction: " + str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=get_jwt_identity()).first()
    if not transaction:
        return jsonify({"error": "Transaction not found or not owned by user"}), 404

    data = request.get_json()
    try:
        if 'amount' in data:
            transaction.amount = float(data.get('amount'))
        if 'type' in data:
            if data.get('type') not in ['income', 'expense']:
                return jsonify({"error": "Invalid transaction type"}), 400
            transaction.type = data.get('type')
        if 'description' in data:
            transaction.description = data.get('description')
        if 'date' in data:
            transaction.date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        if 'category_id' in data:
            category_id = data.get('category_id')
            category = Category.query.filter_by(id=category_id, user_id=get_jwt_identity()).first() # 確保類別屬於當前使用者
            if not category:
                return jsonify({"error": "Category not found or not owned by user"}), 404
            transaction.category_id = category_id

        db.session.commit()
        return jsonify(transaction.to_dict())
    except ValueError:
        return jsonify({"error": "Invalid amount or date format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update transaction: " + str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=get_jwt_identity()).first()
    if not transaction:
        return jsonify({"error": "Transaction not found or not owned by user"}), 404
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transaction deleted successfully"}), 204 # 204 No Content
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete transaction: " + str(e)}), 500

# --- 摘要/統計相關 API (受保護，包含篩選) ---

@app.route('/api/summary', methods=['GET'])
@jwt_required()
def get_summary():
    _ = request.args.get('interval')  # 忽略 interval 參數
    user_id = get_jwt_identity()
    total_income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income').scalar() or 0
    total_expense = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='expense').scalar() or 0

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    })

@app.route('/api/summary/category_breakdown', methods=['GET'])
@jwt_required()
def get_category_breakdown():
    _ = request.args.get('interval')  # 忽略 interval 參數
    transaction_type = request.args.get('type') # 'income' or 'expense'
    # 這裡先把空字串轉成 None
    start_date_str = request.args.get('start_date') or None
    end_date_str = request.args.get('end_date') or None
    if start_date_str is not None and start_date_str.strip() == "":
        start_date_str = None
    if end_date_str is not None and end_date_str.strip() == "":
        end_date_str = None

    query = db.session.query(
        Category.name,
        Category.type,
        func.sum(Transaction.amount)
    ).join(Transaction, Transaction.category_id == Category.id).filter(
        Transaction.user_id == get_jwt_identity(),
        Category.user_id == get_jwt_identity()
    )

    if transaction_type in ['income', 'expense']:
        query = query.filter(Transaction.type == transaction_type)
    if start_date_str is not None:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date_str is not None:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    category_summary = query.group_by(Category.name, Category.type).all()

    summary_by_category = []
    for name, type, total_amount in category_summary:
        summary_by_category.append({
            'category_name': name,
            'type': type,
            'total_amount': total_amount
        })

    return jsonify(summary_by_category)



@app.route('/api/summary/trend', methods=['GET'])
@jwt_required()
def get_trend_data():
    interval = request.args.get('interval', 'month')
    start_date_str = request.args.get('start_date') or None
    end_date_str = request.args.get('end_date') or None
    if start_date_str is not None and start_date_str.strip() == "":
        start_date_str = None
    if end_date_str is not None and end_date_str.strip() == "":
        end_date_str = None

    query = Transaction.query.filter_by(user_id=get_jwt_identity())

    if start_date_str is not None:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date_str is not None:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    # === 修正點：將 func.strftime 改為 func.to_char 並調整格式字串 ===
    if interval == 'day':
        group_by_col = func.to_char(Transaction.date, 'YYYY-MM-DD')
    elif interval == 'week':
        group_by_col = func.to_char(Transaction.date, 'IYYY-IW')
    elif interval == 'month':
        group_by_col = func.to_char(Transaction.date, 'YYYY-MM')
    else:
        return jsonify({"error": "Invalid interval. Must be 'day', 'week', or 'month'."}), 400
    # ================================================================

    income_data = query.with_entities(
        group_by_col.label('period'),
        func.sum(Transaction.amount)
    ).filter(Transaction.type == 'income').group_by('period').order_by('period').all()

    expense_data = query.with_entities(
        group_by_col.label('period'),
        func.sum(Transaction.amount)
    ).filter(Transaction.type == 'expense').group_by('period').order_by('period').all()

    income_map = {item.period: item[1] for item in income_data}
    expense_map = {item.period: item[1] for item in expense_data}

    all_periods = sorted(list(set(income_map.keys()) | set(expense_map.keys())))

    trend_data = []
    for period in all_periods:
        trend_data.append({
            'period': period,
            'income': income_map.get(period, 0),
            'expense': expense_map.get(period, 0),
            'balance': income_map.get(period, 0) - expense_map.get(period, 0)
        })

    return jsonify(trend_data)
# --- 使用者設定 API ---

@app.route('/api/user/username', methods=['PUT'])
@jwt_required()
def update_username():
    data = request.get_json()
    new_username = data.get('new_username')

    if not new_username:
        return jsonify({"error": "新的使用者名稱為必填項"}), 400

    if User.query.filter_by(username=new_username).first():
        return jsonify({"error": "該使用者名稱已被使用"}), 409 # Conflict

    user = User.query.get(get_jwt_identity())
    user.username = new_username

    try:
        db.session.commit()
        return jsonify({"message": "使用者名稱更新成功", "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "使用者名稱更新失敗: " + str(e)}), 500

@app.route('/api/user/password', methods=['PUT'])
@jwt_required()
def update_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"error": "舊密碼和新密碼都為必填項"}), 400

    user = User.query.get(get_jwt_identity())
    if not user.check_password(old_password):
        return jsonify({"error": "舊密碼不正確"}), 401 # Unauthorized

    user.set_password(new_password)
    try:
        db.session.commit()
        return jsonify({"message": "密碼更新成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "密碼更新失敗: " + str(e)}), 500

# 假設你用 Flask
@app.route('/api/transactions/summary')
@jwt_required()
def transactions_summary():
    # 查詢當前登入使用者的收入、支出
    total_income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=get_jwt_identity(), type='income').scalar() or 0
    total_expense = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=get_jwt_identity(), type='expense').scalar() or 0
    balance = total_income - total_expense
    return jsonify({
        "income": total_income,
        "expense": total_expense,
        "balance": balance
    })

# ----------------------------------------------------
# 新增：刪除帳號 API
# ----------------------------------------------------
@app.route('/api/user', methods=['DELETE'])
@jwt_required()
def delete_user_account():
    user_id_to_delete = get_jwt_identity()
    user = User.query.get(user_id_to_delete)

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # 1. 檢查用戶是否是任何群組的成員 (無論角色或狀態，只要有 GroupMember 記錄就不能刪除)
        # 排除自己的創建的那個群組
        active_memberships_count = GroupMember.query.filter_by(user_id=user_id_to_delete, status='accepted').count()
        if active_memberships_count > 0:
            return jsonify({"error": "您仍是某些群組的活躍成員，請先退出所有群組。"}), 400

        # 2. 檢查用戶是否是任何群組的創建者
        # 這個檢查要小心，因為如果用戶是創建者，但群組中沒有其他成員，並且沒有交易，
        # 那理論上應該允許自動刪除該群組。
        # 為了簡化，如果創建了任何群組，就要求用戶先解散。
        created_groups_count = Group.query.filter_by(created_by_user_id=user_id_to_delete).count()
        if created_groups_count > 0:
            return jsonify({"error": "您仍創建了某些群組，請先解散所有由您創建的群組。"}), 400

        # 如果通過了上述檢查，說明用戶沒有群組成員身份，也沒有創建任何群組。
        # 此時可以安全地刪除用戶及其個人相關數據。
        # 確保在模型中設置了 cascade='all, delete-orphan'，或者在這裡手動刪除：
        # - Category (用戶的個人類別)
        # - Transaction (用戶的個人交易)
        # - Invitation (用戶發送的或接收的邀請，這部分通常也會被級聯刪除，或者根據業務邏輯處理)
        # - GroupTransaction (用戶記錄的群組交易，這部分也會被級聯刪除)

        # 假設在 User 模型中，categories 和 transactions 關係設置了 cascade='all, delete-orphan'
        # 示例：categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
        # 如果沒有，則需要手動執行：
        Transaction.query.filter_by(user_id=user_id_to_delete).delete(synchronize_session=False)
        Category.query.filter_by(user_id=user_id_to_delete).delete(synchronize_session=False)
        
        # 刪除發送和接收的邀請 (即使 Invitation 模型沒有 cascade，這裡手動刪除確保乾淨)
        Invitation.query.filter_by(invited_by_user_id=user_id_to_delete).delete(synchronize_session=False)
        Invitation.query.filter_by(invited_user_id=user_id_to_delete).delete(synchronize_session=False)
        
        # 刪除用戶記錄的群組交易
        GroupTransaction.query.filter_by(created_by_user_id=user_id_to_delete).delete(synchronize_session=False)

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "帳號刪除成功"}), 204 # 204 No Content
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user account: {e}")
        return jsonify({"error": "刪除帳號失敗: " + str(e)}), 500

# 運行應用程式
if __name__ == '__main__':
    # Flask-Login 的 Session Protection 預設是 'strong'
    # 這會要求瀏覽器在登入成功後，每次請求都帶上 session_cookie
    app.run(debug=True, port=5000)
