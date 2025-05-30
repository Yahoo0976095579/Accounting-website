# server/app.py
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

app = Flask(__name__)

# --- Flask 配置 ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_development_secret_key_please_change_me') # 確保這裡的值在 .env 中設置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 啟用 CORS，允許前端應用程式訪問
# 在開發階段，可以允許所有來源。生產環境中，請限制為你的前端域名。
CORS(app, supports_credentials=True) # supports_credentials=True 允許發送 cookie/會話憑證

# --- 資料庫初始化 ---
db = SQLAlchemy(app)

# --- Flask-Login 初始化 ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # 未登入時重定向到的視圖名稱

# 使用者載入器：告訴 Flask-Login 如何根據使用者 ID 載入使用者物件
# server/app.py (在 Flask-Login 初始化部分)
@login_manager.user_loader
def load_user(user_id):
    # 推薦的 SQLAlchemy 2.0 寫法
    # 注意：db.session.get() 直接接收主鍵，且不需要 Query 物件
    return db.session.get(User, int(user_id))

# --- 資料庫模型定義 ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 與 Transaction 和 Category 的關係
    categories = db.relationship('Category', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 外鍵，歸屬於特定使用者

    # === 移除原有的 transactions 關係，它現在由 Transaction 端的 backref 管理 ===
    # 例如，如果你有一個類別物件 cat，你可以用 cat.transactions_in_category 訪問屬於它的交易
    # ===========================================================================

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
    # 'transactions_in_category' 是 Category 端用於反向查找交易的屬性名
    category = db.relationship('Category', backref='transactions_in_category', lazy=True)
    # ============================================

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
login_manager.login_view = 'login'

# --- 認證相關 API ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409 # Conflict

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    try:
        db.session.commit()
        # 註冊成功後自動登入
        login_user(new_user)
        # 也可以在這裡為新使用者添加預設類別
        add_default_categories_for_user(new_user.id)
        return jsonify({"message": "User registered and logged in successfully", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
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
        login_user(user) # 登入使用者，將使用者資訊儲存在 session 中
        return jsonify({"message": "Logged in successfully", "user": user.to_dict()}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401 # Unauthorized

@app.route('/api/logout', methods=['GET']) # 確保是 GET 方法
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/user', methods=['GET'])
@login_required # 只有登入後才能獲取使用者資訊
def get_current_user():
    return jsonify(current_user.to_dict()), 200

# --- 類別相關 API (受保護) ---

@app.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return jsonify([c.to_dict() for c in categories])

@app.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    data = request.get_json()
    name = data.get('name')
    category_type = data.get('type')

    if not name or not category_type:
        return jsonify({"error": "Name and type are required"}), 400
    if category_type not in ['income', 'expense']:
        return jsonify({"error": "Invalid category type"}), 400

    # 檢查是否已存在相同名稱的類別給當前使用者
    if Category.query.filter_by(user_id=current_user.id, name=name).first():
        return jsonify({"error": "已存在同名的類別"}), 409

    new_category = Category(name=name, type=category_type, user_id=current_user.id)
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({"error": "已存在同名的類別"}), 404

    data = request.get_json()
    name = data.get('name', category.name)
    category_type = data.get('type', category.type)

    if category_type not in ['income', 'expense']:
        return jsonify({"error": "Invalid category type"}), 400

    # 檢查更新後是否會與同使用者下的其他類別名稱重複
    if Category.query.filter(
        Category.user_id == current_user.id,
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
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({"error": "Category not found or not owned by user"}), 404

    # 檢查是否有交易記錄關聯到此類別
    if Transaction.query.filter_by(category_id=category_id, user_id=current_user.id).first():
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
@login_required
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

    query = Transaction.query.filter_by(user_id=current_user.id)

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
@login_required
def get_transaction(transaction_id):
    # 確保使用者只能查看自己的交易記錄
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not transaction:
        return jsonify({"error": "Transaction not found or not owned by user"}), 404
    return jsonify(transaction.to_dict())

# server/app.py (在 add_transaction 函數內部)
@app.route('/api/transactions', methods=['POST'])
@login_required
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
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
        if not category:
            return jsonify({"error": "Category not found or not owned by user"}), 404

        transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_transaction = Transaction(
            amount=amount,
            type=transaction_type,
            description=description,
            date=transaction_date,
            category_id=category_id,
            user_id=current_user.id # 設置交易記錄的 user_id
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
@login_required
def update_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
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
            category = Category.query.filter_by(id=category_id, user_id=current_user.id).first() # 確保類別屬於當前使用者
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
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
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
@login_required
def get_summary():
    # 獲取總收入和總支出
    total_income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='income').scalar() or 0
    total_expense = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='expense').scalar() or 0

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    })

@app.route('/api/summary/category_breakdown', methods=['GET'])
@login_required
def get_category_breakdown():
    transaction_type = request.args.get('type') # 'income' or 'expense'
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = db.session.query(
        Category.name,
        Category.type,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        Category.user_id == current_user.id # 確保類別也歸屬於當前使用者
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
@login_required
def get_trend_data():
    interval = request.args.get('interval', 'month') # 'day', 'week', 'month'
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = Transaction.query.filter_by(user_id=current_user.id)

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
        group_by_col = func.strftime('%Y-%m-%d', Transaction.date)
    elif interval == 'week':
        # SQLite 的 strftime 處理週數可能複雜，這裡用日期範圍來模擬
        # 更精確的週數計算可能需要自定義函數或更複雜的 SQL
        group_by_col = func.strftime('%Y-%W', Transaction.date) # YYYY-WW (週數從0開始)
    elif interval == 'month':
        group_by_col = func.strftime('%Y-%m', Transaction.date)
    else:
        return jsonify({"error": "Invalid interval. Must be 'day', 'week', or 'month'."}), 400

    # 聚合收入和支出
    income_data = query.with_entities(
        group_by_col.label('period'),
        func.sum(Transaction.amount)
    ).filter(Transaction.type == 'income').group_by('period').order_by('period').all()

    expense_data = query.with_entities(
        group_by_col.label('period'),
        func.sum(Transaction.amount)
    ).filter(Transaction.type == 'expense').group_by('period').order_by('period').all()

    # 將結果轉換為字典，方便前端處理
    income_map = {item.period: item[1] for item in income_data}
    expense_map = {item.period: item[1] for item in expense_data}

    # 合併結果並填充缺失的時期
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


# 運行應用程式
if __name__ == '__main__':
    # Flask-Login 的 Session Protection 預設是 'strong'
    # 這會要求瀏覽器在登入成功後，每次請求都帶上 session_cookie
    app.run(debug=True, port=5000)