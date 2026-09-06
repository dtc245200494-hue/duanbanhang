import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import zipfile

def create_standard_uml_usecase():
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 110)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#FFFFFF')

    # 1. Main Title
    ax.text(80, 105, "SƠ ĐỒ USE CASE TỔNG QUÁT HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP AI", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#1E3A8A')

    # 2. System Boundary Rectangle
    rect = patches.FancyBboxPatch((30, 6), 100, 94, boxstyle="round,pad=0.5,rounding_size=1.5",
                                  edgecolor='#1E3A8A', facecolor='#F8FAFC', lw=2.2, zorder=1)
    ax.add_patch(rect)
    
    # System Name Header inside boundary
    ax.text(80, 96.5, "«system» HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP AI (AI POS)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#0F172A', zorder=2)

    # Helper: Draw Standard UML Stick Figure (Người que chuẩn UML 2.5)
    def draw_stick_actor(x, y, name, role_desc, color='#1E3A8A', bg_head='#DBEAFE'):
        # Head (Circle)
        head = patches.Circle((x, y + 5.0), 2.0, edgecolor=color, facecolor=bg_head, lw=2.4, zorder=5)
        ax.add_patch(head)
        # Torso / Body (Line)
        ax.plot([x, x], [y + 3.0, y - 3.0], color=color, lw=2.8, zorder=5, solid_capstyle='round')
        # Arms (Horizontal Line)
        ax.plot([x - 4.0, x + 4.0], [y + 1.0, y + 1.0], color=color, lw=2.8, zorder=5, solid_capstyle='round')
        # Left Leg
        ax.plot([x, x - 3.2], [y - 3.0, y - 8.5], color=color, lw=2.8, zorder=5, solid_capstyle='round')
        # Right Leg
        ax.plot([x, x + 3.2], [y - 3.0, y - 8.5], color=color, lw=2.8, zorder=5, solid_capstyle='round')
        # Name Box
        ax.text(x, y - 10.5, name, ha='center', va='top', fontsize=12, fontweight='bold', color='#0F172A', zorder=5)
        ax.text(x, y - 13.5, role_desc, ha='center', va='top', fontsize=10.5, fontstyle='italic', color='#475569', zorder=5)

    # Draw Actors
    admin_x, admin_y = 14, 52
    owner_x, owner_y = 146, 52
    
    draw_stick_actor(admin_x, admin_y, "Quản trị viên", "(Admin)", color='#B45309', bg_head='#FEF3C7')
    draw_stick_actor(owner_x, owner_y, "Chủ cửa hàng", "(Owner)", color='#1E3A8A', bg_head='#DBEAFE')

    # Helper: Draw Use Case (Horizontal Ellipse)
    usecases = {}
    
    def draw_usecase(key, cx, cy, text, is_ai=False, is_sub=False):
        w = 30 if not is_sub else 25
        h = 7.0 if not is_sub else 5.8
        bg = '#F0FDF4' if is_ai else ('#FFFFFF' if not is_sub else '#F1F5F9')
        edge = '#10B981' if is_ai else ('#2563EB' if not is_sub else '#64748B')
        lw = 2.0 if not is_sub else 1.6
        
        ellipse = patches.Ellipse((cx, cy), w, h, edgecolor=edge, facecolor=bg, lw=lw, zorder=3)
        ax.add_patch(ellipse)
        
        font_weight = 'bold' if not is_sub else 'normal'
        font_size = 10 if not is_sub else 9
        text_color = '#065F46' if is_ai else '#0F172A'
        
        ax.text(cx, cy, text, ha='center', va='center', fontsize=font_size, 
                fontweight=font_weight, color=text_color, zorder=4, multialignment='center')
        
        usecases[key] = (cx, cy, w, h)

    # 3-Column Balanced Layout:
    # Top Center: Shared Authentication
    draw_usecase("UC1", 80, 87, "Đăng nhập & Xác thực JWT")

    # Left Column (Admin & Backend Focus)
    draw_usecase("UC2", 52, 72, "Quản lý Tài khoản (Admin)")
    draw_usecase("UC3", 52, 57, "Quản lý Danh mục & Sản phẩm")
    draw_usecase("UC4", 52, 42, "Nhập hàng & Quản lý Kho")
    draw_usecase("UC5", 52, 27, "Xem Dashboard Doanh thu")
    draw_usecase("UC6", 52, 13, "Xuất báo cáo Excel / PDF")

    # Right Column (Owner & POS / AI Focus)
    draw_usecase("UC7", 108, 72, "Bán hàng tại quầy (POS)")
    draw_usecase("UC8", 108, 57, "Hủy đơn hàng & Hoàn kho")
    draw_usecase("UC9", 108, 42, "Trợ lý AI: Tư vấn Sản phẩm", is_ai=True)
    draw_usecase("UC10", 108, 27, "Trợ lý AI: Phân tích Doanh thu", is_ai=True)
    draw_usecase("UC_STOCK", 108, 13, "«include»\nCập nhật tồn kho tự động", is_sub=True)

    # 3. Association Lines (Đường thẳng liền nét chuẩn UML - Solid Lines, KHÔNG DÙNG MŨI TÊN)
    def connect_actor_uc(actor_pt, uc_key, line_color='#64748B', is_left=True):
        cx, cy, w, h = usecases[uc_key]
        edge_x = cx - w/2 if is_left else cx + w/2
        edge_y = cy
        ax.plot([actor_pt[0], edge_x], [actor_pt[1], edge_y], color=line_color, lw=1.8, zorder=2)

    admin_pt = (admin_x + 4.5, admin_y)
    owner_pt = (owner_x - 4.5, owner_y)

    # Admin Associations (Quản trị viên kết nối UC1, UC2, UC3, UC4, UC5, UC6, UC10)
    admin_color = '#D97706'
    connect_actor_uc(admin_pt, "UC1", admin_color, is_left=True)
    connect_actor_uc(admin_pt, "UC2", admin_color, is_left=True)
    connect_actor_uc(admin_pt, "UC3", admin_color, is_left=True)
    connect_actor_uc(admin_pt, "UC4", admin_color, is_left=True)
    connect_actor_uc(admin_pt, "UC5", admin_color, is_left=True)
    connect_actor_uc(admin_pt, "UC6", admin_color, is_left=True)
    # Admin can also use AI analytics
    ax.plot([admin_pt[0], 93], [admin_pt[1], 27], color=admin_color, lw=1.5, zorder=2)

    # Owner Associations (Chủ cửa hàng kết nối UC1, UC3, UC4, UC5, UC6, UC7, UC8, UC9, UC10)
    owner_color = '#2563EB'
    connect_actor_uc(owner_pt, "UC1", owner_color, is_left=False)
    connect_actor_uc(owner_pt, "UC7", owner_color, is_left=False)
    connect_actor_uc(owner_pt, "UC8", owner_color, is_left=False)
    connect_actor_uc(owner_pt, "UC9", owner_color, is_left=False)
    connect_actor_uc(owner_pt, "UC10", owner_color, is_left=False)
    # Owner can also access products, warehouse, dashboard
    ax.plot([owner_pt[0], 67], [owner_pt[1], 57], color=owner_color, lw=1.5, zorder=2)
    ax.plot([owner_pt[0], 67], [owner_pt[1], 42], color=owner_color, lw=1.5, zorder=2)
    ax.plot([owner_pt[0], 67], [owner_pt[1], 27], color=owner_color, lw=1.5, zorder=2)

    # 4. UML <<include>> Relationships (Dashed Line with Open Arrow)
    # Direct short relationship from POS (UC7) to UC_STOCK
    ax.annotate("", xy=(108, 16.5), xytext=(108, 68.5),
                arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5, linestyle="dashed"))
    ax.text(109.5, 35, "«include»", fontsize=8.5, fontstyle='italic', color='#475569', ha='left', zorder=5)

    # 5. Legend / Chú thích chuẩn UML 2.5
    leg_box = patches.FancyBboxPatch((32, 7.5), 38, 7.0, boxstyle="round,pad=0.3,rounding_size=0.8",
                                     edgecolor='#CBD5E1', facecolor='#FFFFFF', lw=1.2, zorder=6)
    ax.add_patch(leg_box)
    ax.text(33.5, 12.8, "Quy ước chuẩn UML 2.5:", fontsize=9, fontweight='bold', color='#1E293B', zorder=7)
    ax.plot([33.5, 41], [10.3, 10.3], color='#2563EB', lw=1.8, zorder=7)
    ax.text(42, 10.3, "Association (Đường liên kết không mũi tên)", fontsize=8, color='#334155', va='center', zorder=7)
    ax.plot([33.5, 41], [8.5, 8.5], color='#475569', lw=1.5, linestyle='dashed', zorder=7)
    ax.text(42, 8.5, "«include» (Quan hệ phụ thuộc bắt buộc)", fontsize=8, color='#334155', va='center', zorder=7)

    # Save to all image destinations
    out_paths = [
        "d:/duanbanhang/tailieu/images/01_use_case.png",
        "d:/duanbanhang/tailieu/images/image1.png",
        "d:/duanbanhang/docs/images/01_use_case.png",
        "d:/duanbanhang/docs/images/image1.png"
    ]
    
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
        print(f"Saved: {p}")

    plt.close()

    # Update docx files
    def update_docx_images(docx_path):
        temp_docx = docx_path + '.temp.docx'
        with zipfile.ZipFile(docx_path, 'r') as zin:
            with zipfile.ZipFile(temp_docx, 'w', zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == 'word/media/image1.png':
                        with open('d:/duanbanhang/tailieu/images/image1.png', 'rb') as f:
                            zout.writestr(item, f.read())
                    else:
                        zout.writestr(item, zin.read(item.filename))
        os.replace(temp_docx, docx_path)
        print(f"Updated image1 in {docx_path}")

    try:
        update_docx_images('d:/duanbanhang/docs/BaoCao_TongHop_QuanLyBanHang_AI_Nhom03.docx')
    except Exception as e:
        print("docs error:", e)

    try:
        update_docx_images('d:/duanbanhang/tailieu/BAO_CAO_KT1_NHOM03_MOI.docx')
    except Exception as e:
        print("tailieu error:", e)

if __name__ == "__main__":
    create_standard_uml_usecase()
