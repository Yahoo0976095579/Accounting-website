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
    is_active = db.Column(db.Boolean, nullable=False, default=True) # <-- 確保這行存在並設置為 True

    # 與 Transaction 和 Category 的關係 (保持不變)
    categories = db.relationship('Category', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    # <-- 新增或確保以下群組相關的關係定義
    # Group.created_by_user_id (創建的群組)
    created_groups = db.relationship('Group', foreign_keys='Group.created_by_user_id', backref='creator', lazy=True)
    # GroupMember (所屬的群組成員身份)
    group_memberships = db.relationship('GroupMember', backref='member_user', lazy=True)
    # Invitation (發送的邀請)
    sent_invitations = db.relationship('Invitation', foreign_keys='Invitation.invited_by_user_id', backref='sender', lazy=True)
    # Invitation (收到的邀請)
    received_invitations = db.relationship('Invitation', foreign_keys='Invitation.invited_user_id', backref='receiver', lazy=True)
    # GroupTransaction (在群組中記錄的交易)
    recorded_group_transactions = db.relationship('GroupTransaction', foreign_keys='GroupTransaction.created_by_user_id', backref='creator', lazy=True)
    # --> 結束新增或確認

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # UserMixin 默認需要這些屬性
    # @property
    # def is_active(self):
    #     return True # 已經通過 is_active 欄位處理，所以這個屬性方法可以移除或確保其簡單返回 True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active # 確保這裡也包含
        }

# server/app.py (在 Category 模型內部)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 外鍵，歸屬於特定使用者

       # 修正這行：將 backref 改為不會衝突的名稱
    transactions_in_category = db.relationship('Transaction', backref='personal_transactions_from_category', lazy=True)

    # <-- 新增這行：與 GroupTransaction 的關係
    group_transactions_with_category = db.relationship('GroupTransaction', backref='category', lazy=True)
    # --> 結束新增

    def __repr__(self):
        return f"Category('{self.name}', '{self.type}', User_id: {self.user_id})"

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
    date = db.Column(db.Date, nullable=False) # 交易日期
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # 記錄創建時間
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 外鍵，歸屬於特定使用者

    # === 新增這行，明確定義與 Category 的關聯 ===
    # 修正這行：將 backref 改為不會衝突的名稱
    category = db.relationship('Category', backref='related_transactions_via_category_fk', lazy=True)

    def __repr__(self):
        return f"Transaction('{self.amount}', '{self.type}', '{self.date}', User_id: {self.user_id})"

    def to_dict(self):
        # 這裡就不需要複雜的 if/else 判斷和查詢了，因為 category 屬性應該會存在
        # 並且在 refresh 後會被加載
        return {
            'id': self.id,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None, # 這裡現在應該能正確訪問 category 屬性了
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
        db.session.commit()

        # 也可以在這裡為新使用者添加預設類別
        add_default_categories_for_user(new_user.id)
        return jsonify({"message": "User registered and logged in successfully", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print("Registration failed:", e)  # 這行會印出詳細錯誤到 log
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

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "message": "Logged in successfully",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
    else:
        return jsonify({"error": "名稱或密碼錯誤"}), 401

@app.route('/api/logout', methods=['GET']) # 確保是 GET 方法
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/user', methods=['GET'])
@jwt_required() # 只有登入後才能獲取使用者資訊

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

@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    # 檢查使用者是否為群組管理員
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), role='admin', status='accepted').first()
    if not group_member:
        return jsonify({"error": "群組未找到或您無權刪除該群組"}), 403 # Forbidden

    group = group_member.group

    # 檢查是否有成員或交易關聯
    if group.group_members.count() > 1: # 如果還有其他成員（除了創建者自己）
        return jsonify({"error": "群組中仍有其他成員，無法直接刪除"}), 400
    if GroupTransaction.query.filter_by(group_id=group_id).first():
        return jsonify({"error": "群組中仍有交易記錄，無法直接刪除"}), 400

    try:
        # 刪除所有相關的 GroupMember 記錄 (包括創建者自己的)
        GroupMember.query.filter_by(group_id=group_id).delete()
        db.session.delete(group)
        db.session.commit()
        return jsonify({"message": "群組刪除成功"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "群組刪除失敗: " + str(e)}), 500

@app.route('/api/groups/<int:group_id>/leave', methods=['POST'])
@jwt_required()
def leave_group(group_id):
    # 查找使用者在該群組的成員身份
    group_member = GroupMember.query.filter_by(group_id=group_id, user_id=get_jwt_identity(), status='accepted').first()
    if not group_member:
        return jsonify({"error": "您不是該群組成員"}), 404

    # 如果是群組唯一管理員且還有其他成員，不能直接退出
    if group_member.role == 'admin' and GroupMember.query.filter_by(group_id=group_id, role='admin', status='accepted').count() == 1 and GroupMember.query.filter_by(group_id=group_id, status='accepted').count() > 1:
        return jsonify({"error": "您是該群組的唯一管理員，請先轉移管理權限或移除其他成員再退出"}), 400

    try:
        db.session.delete(group_member)
        db.session.commit()
        return jsonify({"message": "已成功退出群組"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "退出群組失敗: " + str(e)}), 500


# --- 群組邀請 API ---

@app.route('/api/groups/<int:group_id>/invite', methods=['POST'])
@jwt_required()
def invite_member(group_id):
    # 檢查使用者是否為群組管理員
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

    # 檢查是否已經是成員
    if GroupMember.query.filter_by(group_id=group_id, user_id=invited_user.id, status='accepted').first():
        return jsonify({"error": "該使用者已是群組成員"}), 409

    # 檢查是否已有待處理邀請
    if Invitation.query.filter_by(group_id=group_id, invited_user_id=invited_user.id, status='pending').first():
        return jsonify({"error": "已存在對該使用者的待處理邀請"}), 409

    new_invitation = Invitation(
        group_id=group_id,
        invited_by_user_id=get_jwt_identity(),
        invited_user_id=invited_user.id,
        status='pending'
    )
    try:
        db.session.add(new_invitation)
        db.session.commit()
        return jsonify({"message": f"已成功向 {invited_username} 發送邀請"}), 201
    except Exception as e:
        db.session.rollback()
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

    interval = request.args.get('interval', 'month') # 'day', 'week', 'month'
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = GroupTransaction.query.filter_by(group_id=group_id) # <-- 關鍵：按 group_id 篩選

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

    if interval == 'day':
        group_by_col = func.strftime('%Y-%m-%d', GroupTransaction.date)
    elif interval == 'week':
        group_by_col = func.strftime('%Y-%W', GroupTransaction.date)
    elif interval == 'month':
        group_by_col = func.strftime('%Y-%m', GroupTransaction.date)
    else:
        return jsonify({"error": "Invalid interval. Must be 'day', 'week', or 'month'."}), 400

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
    transaction_type = request.args.get('type') # 'income' or 'expense'
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = db.session.query(
        Category.name,
        Category.type,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.user_id == get_jwt_identity(),
        Category.user_id == get_jwt_identity() # 確保類別也歸屬於當前使用者
    )

    if transaction_type in ['income', 'expense']:
        query = query.filter(Transaction.type == transaction_type)
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
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = Transaction.query.filter_by(user_id=get_jwt_identity())

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

    # 根據 interval 進行分組
    if interval == 'day':
        group_by_col = func.to_char(Transaction.date, 'YYYY-MM-DD')
    elif interval == 'week':
        group_by_col = func.to_char(Transaction.date, 'IYYY-IW')  # ISO週
    elif interval == 'month':
        group_by_col = func.to_char(Transaction.date, 'YYYY-MM')
    else:
        return jsonify({"error": "Invalid interval. Must be 'day', 'week', or 'month'."}), 400

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

# 運行應用程式
if __name__ == '__main__':
    # Flask-Login 的 Session Protection 預設是 'strong'
    # 這會要求瀏覽器在登入成功後，每次請求都帶上 session_cookie
    app.run(debug=True, port=5000)
