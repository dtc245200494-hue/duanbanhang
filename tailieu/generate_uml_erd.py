import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import zipfile
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')

def create_erd_diagram():
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(19, 11), dpi=300)
    ax.set_xlim(0, 190)
    ax.set_ylim(0, 110)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Main Title
    ax.text(95, 106, "SƠ ĐỒ QUAN HỆ THỰC THỂ CSDL (ERD - 7 BẢNG CỐT LÕI SALES.DB)", 
            ha='center', va='center', fontsize=16.5, fontweight='bold', color='#1E3A8A')

    # Draw standard ERD table box
    def draw_erd_table(x, y, w, h, table_name, columns):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.8",
                                      edgecolor='#3B82F6', facecolor='#FFFFFF', lw=1.8, zorder=3)
        ax.add_patch(rect)
        
        # Header
        header_h = 4.2
        header_rect = patches.Rectangle((x, y + h - header_h), w, header_h, 
                                        facecolor='#1E3A8A', edgecolor='none', zorder=4)
        ax.add_patch(header_rect)
        
        ax.text(x + w/2, y + h - header_h/2, table_name, ha='center', va='center', 
                fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=5)
        
        # Separator line
        ax.plot([x, x + w], [y + h - header_h, y + h - header_h], color='#3B82F6', lw=1.5, zorder=5)
        
        # Columns
        curr_y = y + h - header_h - 2.2
        for col, col_type, key in columns:
            if key == 'PK':
                color = '#B91C1C'
                prefix = 'PK '
                weight = 'bold'
            elif key == 'FK':
                color = '#1D4ED8'
                prefix = 'FK '
                weight = 'bold'
            elif key == 'UK':
                color = '#0F172A'
                prefix = 'UK '
                weight = 'normal'
            else:
                color = '#334155'
                prefix = '   '
                weight = 'normal'
            
            line_str = f"{prefix}{col} : {col_type}"
            ax.text(x + 1.2, curr_y, line_str, ha='left', va='center', fontsize=8.2, fontweight=weight, color=color, zorder=5)
            curr_y -= 2.0

    # ROW 1 (y: 65)
    # 1. USERS
    draw_erd_table(10, 68, 36, 26, "USERS", [
        ("id", "integer", "PK"),
        ("username", "varchar(50)", "UK"),
        ("password_hash", "varchar(255)", ""),
        ("full_name", "varchar(100)", ""),
        ("role", "varchar(20)", ""),
        ("is_active", "boolean", ""),
        ("created_at", "timestamp", "")
    ])

    # 2. CATEGORIES
    draw_erd_table(56, 76, 34, 18, "CATEGORIES", [
        ("id", "integer", "PK"),
        ("name", "varchar(100)", "UK"),
        ("description", "text", "")
    ])

    # 3. PRODUCTS
    draw_erd_table(102, 64, 36, 32, "PRODUCTS", [
        ("id", "integer", "PK"),
        ("code", "varchar(50)", "UK"),
        ("name", "varchar(200)", ""),
        ("category_id", "integer", "FK"),
        ("import_price", "decimal(12,2)", ""),
        ("sell_price", "decimal(12,2)", ""),
        ("stock", "integer", ""),
        ("status", "varchar(20)", ""),
        ("description", "text", "")
    ])

    # 4. INVENTORIES
    draw_erd_table(148, 76, 32, 18, "INVENTORIES", [
        ("id", "integer", "PK"),
        ("product_id", "integer", "FK"),
        ("quantity", "integer", "")
    ])

    # ROW 2 (y: 15..20)
    # 5. CUSTOMERS
    draw_erd_table(10, 18, 36, 25, "CUSTOMERS", [
        ("id", "integer", "PK"),
        ("name", "varchar(100)", ""),
        ("phone", "varchar(20)", "UK"),
        ("email", "varchar(100)", ""),
        ("address", "text", ""),
        ("customer_group", "varchar(50)", "")
    ])

    # 6. ORDERS
    draw_erd_table(56, 14, 36, 33, "ORDERS", [
        ("id", "integer", "PK"),
        ("code", "varchar(50)", "UK"),
        ("customer_id", "integer", "FK"),
        ("user_id", "integer", "FK"),
        ("total_amount", "decimal(12,2)", ""),
        ("discount", "decimal(12,2)", ""),
        ("final_amount", "decimal(12,2)", ""),
        ("payment_method", "varchar(30)", ""),
        ("status", "varchar(20)", ""),
        ("created_at", "timestamp", "")
    ])

    # 7. ORDER_DETAILS
    draw_erd_table(102, 20, 36, 25, "ORDER_DETAILS", [
        ("id", "integer", "PK"),
        ("order_id", "integer", "FK"),
        ("product_id", "integer", "FK"),
        ("quantity", "integer", ""),
        ("price", "decimal(12,2)", ""),
        ("total", "decimal(12,2)", "")
    ])

    # 8. PURCHASE_RECEIPTS
    draw_erd_table(148, 20, 32, 25, "PURCHASE_RECEIPTS", [
        ("id", "integer", "PK"),
        ("code", "varchar(50)", "UK"),
        ("supplier", "varchar(150)", ""),
        ("user_id", "integer", "FK"),
        ("total_amount", "decimal(12,2)", ""),
        ("status", "varchar(20)", ""),
        ("created_at", "timestamp", "")
    ])

    # ---------------- RELATIONSHIPS & ARROWS ----------------
    # 1. CATEGORIES (1) ───► (1..N) PRODUCTS
    ax.plot([90, 102], [85, 85], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(102, 85), xytext=(98, 85),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(91, 86.5, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(98, 86.5, "1..N", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(96, 82.5, "phân loại", fontsize=8, color='#475569', ha='center')

    # 2. PRODUCTS (1) ───► (1..1) INVENTORIES
    ax.plot([138, 148], [85, 85], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(148, 85), xytext=(144, 85),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(138.5, 86.5, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(144, 86.5, "1..1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(143, 82.5, "tồn kho", fontsize=8, color='#475569', ha='center')

    # 3. CUSTOMERS (1) ───► (0..N) ORDERS
    ax.plot([46, 56], [30, 30], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(56, 30), xytext=(52, 30),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(46.5, 31.5, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(52, 31.5, "0..N", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(51, 27.5, "đặt mua", fontsize=8, color='#475569', ha='center')

    # 4. ORDERS (1) ───► (1..N) ORDER_DETAILS
    ax.plot([92, 102], [30, 30], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(102, 30), xytext=(98, 30),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(92.5, 31.5, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(98, 31.5, "1..N", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(97, 27.5, "chi tiết", fontsize=8, color='#475569', ha='center')

    # 5. PRODUCTS (1) ───► (0..N) ORDER_DETAILS
    ax.plot([120, 120], [64, 45], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(120, 45), xytext=(120, 49),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(121, 60, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(121, 47, "0..N", fontsize=9.5, fontweight='bold', color='#1D4ED8')

    # 6. USERS (1) ───► (0..N) ORDERS (Lập đơn - qua khe giữa)
    ax.plot([36, 40, 40, 74, 74], [80, 80, 55, 55, 47], color='#D97706', lw=2.0)
    ax.annotate("", xy=(74, 47), xytext=(74, 51),
                arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.0))
    ax.text(36.5, 81.5, "1", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(75, 48, "0..N", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(57, 56.5, "lập đơn (FK user_id)", fontsize=8, color='#B45309', ha='center')

    # 7. USERS (1) ───► (0..N) PURCHASE_RECEIPTS (Nhập kho)
    ax.plot([28, 28, 164, 164], [68, 52, 52, 45], color='#D97706', lw=2.0)
    ax.annotate("", xy=(164, 45), xytext=(164, 49),
                arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.0))
    ax.text(29, 64, "1", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(165, 47, "0..N", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(140, 53.5, "nhập kho (FK user_id)", fontsize=8, color='#B45309', ha='center')

    out_paths = [
        f"{BASE_DIR}/tailieu/images/03_erd.png",
        f"{BASE_DIR}/tailieu/images/image3.png",
        f"{BASE_DIR}/docs/images/03_erd.png",
        f"{BASE_DIR}/docs/images/image3.png"
    ]
    
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
        print(f"Saved: {p}")

    plt.close()

    # Update docx image3
    try:
        docx_path = f'{BASE_DIR}/docs/BaoCao_TongHop_QuanLyBanHang_AI_Nhom03.docx'
        temp_docx = docx_path + '.temp.docx'
        with zipfile.ZipFile(docx_path, 'r') as zin:
            with zipfile.ZipFile(temp_docx, 'w', zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == 'word/media/image3.png':
                        with open(f'{BASE_DIR}/tailieu/images/image3.png', 'rb') as f:
                            zout.writestr(item, f.read())
                    else:
                        zout.writestr(item, zin.read(item.filename))
        os.replace(temp_docx, docx_path)
        print(f"Updated image3 in {docx_path}")
    except Exception as e:
        print("docx update error:", e)

if __name__ == "__main__":
    create_erd_diagram()