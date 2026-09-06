import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import zipfile

def create_domain_class_diagram():
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(19, 11), dpi=300)
    ax.set_xlim(0, 190)
    ax.set_ylim(0, 110)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')

    # Main Title
    ax.text(95, 106, "SƠ ĐỒ LỚP LĨNH VỰC & THỰC THỂ HỆ THỐNG (DOMAIN CLASS DIAGRAM)", 
            ha='center', va='center', fontsize=16.5, fontweight='bold', color='#1E3A8A')

    # Helper: Draw standard 3-compartment UML Class Box
    def draw_uml_class(x, y, w, h, class_name, attributes, methods=[], header_bg='#1E3A8A', is_service=False):
        border_color = '#1E3A8A' if not is_service else '#059669'
        box_bg = '#FFFFFF' if not is_service else '#F0FDF4'
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.8",
                                      edgecolor=border_color, facecolor=box_bg, lw=1.8, zorder=3)
        ax.add_patch(rect)
        
        # Header (Class Name)
        header_h = 4.4
        header_rect = patches.Rectangle((x, y + h - header_h), w, header_h, 
                                        facecolor=header_bg, edgecolor='none', zorder=4)
        ax.add_patch(header_rect)
        
        stereo = "«entity» " if not is_service else "«service» "
        ax.text(x + w/2, y + h - header_h/2, stereo + class_name, ha='center', va='center', 
                fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=5)
        
        # Separator line 1
        ax.plot([x, x + w], [y + h - header_h, y + h - header_h], color=border_color, lw=1.5, zorder=5)
        
        # Attributes
        curr_y = y + h - header_h - 2.2
        for attr in attributes:
            ax.text(x + 1.2, curr_y, attr, ha='left', va='center', fontsize=8.2, color='#1E293B', zorder=5)
            curr_y -= 2.0
            
        # Methods
        if methods:
            ax.plot([x, x + w], [curr_y + 0.8, curr_y + 0.8], color=border_color, lw=1.2, zorder=5)
            curr_y -= 1.2
            for m in methods:
                ax.text(x + 1.2, curr_y, m, ha='left', va='center', fontsize=8.2, fontstyle='italic', color='#0F172A', zorder=5)
                curr_y -= 2.0

    # ROW 1 (y: 65)
    # 1. USER (Top Left)
    draw_uml_class(10, 68, 36, 28, "User", [
        "+ id: int [PK]",
        "+ username: str [UK]",
        "+ password_hash: str",
        "+ full_name: str",
        "+ role: str",
        "+ is_active: bool",
        "+ created_at: datetime"
    ], [
        "+ verify_password(pwd): bool",
        "+ is_admin(): bool"
    ])

    # 2. CATEGORY (Top Center Left)
    draw_uml_class(56, 75, 34, 18, "Category", [
        "+ id: int [PK]",
        "+ name: str [UK]",
        "+ description: str"
    ], [
        "+ get_active_products(): list"
    ])

    # 3. PRODUCT (Top Center Right)
    draw_uml_class(102, 64, 36, 32, "Product", [
        "+ id: int [PK]",
        "+ code: str [UK]",
        "+ name: str",
        "+ category_id: int [FK]",
        "+ import_price: float",
        "+ sell_price: float",
        "+ stock: int",
        "+ status: str",
        "+ description: str"
    ], [
        "+ check_stock(qty): bool",
        "+ update_stock(qty): void"
    ])

    # 4. AI SERVICE (Top Right)
    draw_uml_class(148, 75, 32, 21, "AIService", [
        "- api_key: str",
        "- model: str"
    ], [
        "+ consult_products(q): str",
        "+ analyze_revenue(): str",
        "- _mask_sensitive(d): dict"
    ], header_bg='#059669', is_service=True)

    # ROW 2 (y: 15..20)
    # 5. PURCHASE RECEIPT (Bottom Left)
    draw_uml_class(10, 18, 36, 26, "PurchaseReceipt", [
        "+ id: int [PK]",
        "+ code: str [UK]",
        "+ supplier: str",
        "+ user_id: int [FK]",
        "+ total_amount: float",
        "+ status: str",
        "+ created_at: datetime"
    ], [
        "+ confirm_receipt(): void"
    ])

    # 6. CUSTOMER (Bottom Center Left)
    draw_uml_class(56, 18, 34, 25, "Customer", [
        "+ id: int [PK]",
        "+ name: str",
        "+ phone: str [UK]",
        "+ email: str",
        "+ address: str",
        "+ customer_group: str"
    ], [
        "+ get_order_history(): list"
    ])

    # 7. ORDER (Bottom Center Right)
    draw_uml_class(102, 13, 36, 34, "Order", [
        "+ id: int [PK]",
        "+ code: str [UK]",
        "+ customer_id: int [FK]",
        "+ user_id: int [FK]",
        "+ total_amount: float",
        "+ discount: float",
        "+ final_amount: float",
        "+ payment_method: str",
        "+ status: str",
        "+ created_at: datetime"
    ], [
        "+ calculate_total(): float",
        "+ cancel_and_refund(): bool"
    ])

    # 8. ORDER DETAIL (Bottom Right)
    draw_uml_class(148, 20, 32, 25, "OrderDetail", [
        "+ id: int [PK]",
        "+ order_id: int [FK]",
        "+ product_id: int [FK]",
        "+ quantity: int",
        "+ price: float",
        "+ total: float"
    ], [
        "+ subtotal(): float"
    ])

    # -------------------------------------------------------------
    # RELATIONSHIPS WITH PROPER UML ARROWS & MULTIPLICITY
    # -------------------------------------------------------------

    # 1. Category 1 ─── 0..* Product (Association)
    ax.plot([90, 102], [84, 84], color='#2563EB', lw=2.0)
    ax.text(91, 85.5, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(98.5, 85.5, "0..*", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(96, 81.5, "chứa", fontsize=8, color='#475569', ha='center')

    # 2. Order 1 ◆─── 1..* OrderDetail (COMPOSITION)
    diamond = patches.Polygon([[138, 30], [139.5, 31.5], [141, 30], [139.5, 28.5]], 
                              closed=True, edgecolor='#1E3A8A', facecolor='#1E3A8A', lw=1.5, zorder=6)
    ax.add_patch(diamond)
    ax.plot([141, 148], [30, 30], color='#1E3A8A', lw=2.0)
    ax.text(141.5, 31.5, "1", fontsize=9.5, fontweight='bold', color='#1E3A8A')
    ax.text(144.5, 31.5, "1..*", fontsize=9.5, fontweight='bold', color='#1E3A8A')
    ax.text(144.5, 27.5, "«composition»", fontsize=7.5, fontstyle='italic', color='#475569', ha='center')

    # 3. Product 1 ───► 0..* OrderDetail (Association)
    ax.plot([138, 143, 143, 148], [75, 75, 40, 40], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(148, 40), xytext=(144, 40),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(138.5, 76.5, "1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(144, 41.5, "0..*", fontsize=9.5, fontweight='bold', color='#1D4ED8')

    # 4. Customer 0..1 ───► 0..* Order
    ax.plot([90, 102], [30, 30], color='#2563EB', lw=2.0)
    ax.annotate("", xy=(102, 30), xytext=(98, 30),
                arrowprops=dict(arrowstyle="->", color="#2563EB", lw=2.0))
    ax.text(91, 31.5, "0..1", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(98, 31.5, "0..*", fontsize=9.5, fontweight='bold', color='#1D4ED8')
    ax.text(96, 27.5, "đặt mua", fontsize=8, color='#475569', ha='center')

    # 5. User 1 ───► 0..* Order (Đi qua khe giữa y: 55, không cắt qua Category hay Customer!)
    ax.plot([46, 50, 50, 120, 120], [80, 80, 55, 55, 47], color='#D97706', lw=2.0)
    ax.annotate("", xy=(120, 47), xytext=(120, 51),
                arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.0))
    ax.text(46.5, 81.5, "1", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(121, 48, "0..*", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(85, 57, "lập đơn hàng (creates order)", fontsize=8.5, fontweight='bold', color='#B45309', ha='center')

    # 6. User 1 ───► 0..* PurchaseReceipt (Nhập kho)
    ax.plot([28, 28], [68, 44], color='#D97706', lw=2.0)
    ax.annotate("", xy=(28, 44), xytext=(28, 49),
                arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.0))
    ax.text(29.5, 65, "1", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(29.5, 46, "0..*", fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(22, 56, "nhập kho", fontsize=8, color='#B45309', ha='right')

    # 7. AIService ─ ─ ─► Product («use»)
    ax.plot([148, 138], [85, 85], color='#059669', lw=1.8, linestyle="dashed")
    ax.annotate("", xy=(138, 85), xytext=(142, 85),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8, linestyle="dashed"))
    ax.text(143, 87, "«use»", fontsize=8, fontstyle='italic', color='#059669', ha='center')

    # 8. AIService ─ ─ ─► Order («analyze»: Đi mép ngoài)
    ax.plot([180, 185, 185, 125, 125], [85, 85, 5, 5, 13], color='#059669', lw=1.6, linestyle="dashed")
    ax.annotate("", xy=(125, 13), xytext=(125, 9),
                arrowprops=dict(arrowstyle="->", color="#059669", lw=1.6, linestyle="dashed"))
    ax.text(155, 7, "«analyze»", fontsize=8, fontstyle='italic', color='#059669', ha='center')

    # Save to all image destinations
    out_paths = [
        "d:/duanbanhang/tailieu/images/02_class_diagram.png",
        "d:/duanbanhang/tailieu/images/image2.png",
        "d:/duanbanhang/docs/images/02_class_diagram.png",
        "d:/duanbanhang/docs/images/image2.png"
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
                    if item.filename == 'word/media/image2.png':
                        with open('d:/duanbanhang/tailieu/images/image2.png', 'rb') as f:
                            zout.writestr(item, f.read())
                    else:
                        zout.writestr(item, zin.read(item.filename))
        os.replace(temp_docx, docx_path)
        print(f"Updated image2 in {docx_path}")

    try:
        update_docx_images('d:/duanbanhang/docs/BaoCao_TongHop_QuanLyBanHang_AI_Nhom03.docx')
    except Exception as e:
        print("docs error:", e)

    print("Domain Class Diagram updated successfully!")

if __name__ == "__main__":
    create_domain_class_diagram()
