"""visualize_product.py - Biểu đồ phân tích theo sản phẩm"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


class ProductVisualizer:
    def __init__(self, df):
        self.df = df
        self.output_dir = 'output/charts'
        os.makedirs(self.output_dir, exist_ok=True)

        # Thiết lập style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")

    def plot_product_quantity(self, top_n=10, figsize=(12, 8)):
        """Biểu đồ số lượng sản phẩm bán ra"""
        if 'Product_Name' not in self.df.columns or 'Quantity' not in self.df.columns:
            print("Thiếu cột Product_Name hoặc Quantity!")
            return False

        # Tính toán dữ liệu
        product_qty = self.df.groupby('Product_Name')['Quantity'].sum().reset_index()
        product_qty = product_qty.sort_values('Quantity', ascending=False)

        # Lấy top N sản phẩm
        top_products = product_qty.head(top_n)

        # Tạo biểu đồ
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Horizontal bar chart
        bars = ax1.barh(top_products['Product_Name'], top_products['Quantity'],
                        color=sns.color_palette("Blues_r", top_n))
        ax1.set_xlabel('Số lượng', fontsize=12)
        ax1.set_title(f'Top {top_n} sản phẩm bán chạy nhất', fontsize=14, fontweight='bold')
        ax1.invert_yaxis()

        # Thêm giá trị trên cột
        for i, (bar, qty) in enumerate(zip(bars, top_products['Quantity'])):
            ax1.text(qty + 5, bar.get_y() + bar.get_height() / 2,
                     f'{qty:,}', va='center', fontsize=10)

        # Pie chart cho phân phối
        ax2.pie(top_products['Quantity'], labels=top_products['Product_Name'],
                autopct='%1.1f%%', startangle=90,
                colors=sns.color_palette("Set3", top_n))
        ax2.set_title(f'Phân phối top {top_n} sản phẩm', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/top_products_quantity.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ sản phẩm: {self.output_dir}/top_products_quantity.png")
        return True

    def plot_product_revenue(self, top_n=10, figsize=(14, 6)):
        """Biểu đồ doanh thu theo sản phẩm"""
        if 'Product_Name' not in self.df.columns or 'Revenue' not in self.df.columns:
            print(" Thiếu cột Product_Name hoặc Revenue!")
            return False

        # Tính toán dữ liệu
        product_rev = self.df.groupby('Product_Name')['Revenue'].sum().reset_index()
        product_rev = product_rev.sort_values('Revenue', ascending=False)

        # Lấy top N sản phẩm
        top_products = product_rev.head(top_n)

        # Tạo biểu đồ
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Bar chart
        x = range(len(top_products))
        bars = ax1.bar(x, top_products['Revenue'] / 1e6,
                       color=sns.color_palette("viridis", top_n))
        ax1.set_xlabel('Sản phẩm', fontsize=12)
        ax1.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax1.set_title(f'Top {top_n} sản phẩm doanh thu cao nhất', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(top_products['Product_Name'], rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')

        # Thêm giá trị trên cột
        for bar, revenue in zip(bars, top_products['Revenue'] / 1e6):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{revenue:,.1f}', ha='center', va='bottom', fontsize=10)

        # Scatter plot: Số lượng vs Doanh thu
        product_stats = self.df.groupby('Product_Name').agg({
            'Quantity': 'sum',
            'Revenue': 'sum',
            'Actual_Selling_Price': 'mean'
        }).reset_index()

        scatter = ax2.scatter(product_stats['Quantity'], product_stats['Revenue'] / 1e6,
                              s=product_stats['Actual_Selling_Price'] / 1000,
                              c=product_stats['Actual_Selling_Price'],
                              cmap='plasma', alpha=0.7, edgecolors='black')

        ax2.set_xlabel('Số lượng bán', fontsize=12)
        ax2.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax2.set_title('Mối quan hệ Số lượng - Doanh thu', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Thêm colorbar
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Giá bán trung bình (VND)', fontsize=10)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/top_products_revenue.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ doanh thu sản phẩm: {self.output_dir}/top_products_revenue.png")
        return True

    def plot_size_distribution(self, figsize=(14, 8)):
        """Biểu đồ phân bổ kích cỡ sản phẩm"""
        if 'Product_Name' not in self.df.columns or 'Size' not in self.df.columns:
            print("Thiếu cột Product_Name hoặc Size!")
            return False

        # Tạo pivot table
        size_pivot = self.df.pivot_table(
            index='Product_Name',
            columns='Size',
            values='Quantity',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        # Đảm bảo có đủ cột
        for size in ['S', 'M', 'L']:
            if size not in size_pivot.columns:
                size_pivot[size] = 0

        # Sắp xếp theo tổng số lượng
        size_pivot['Total'] = size_pivot[['S', 'M', 'L']].sum(axis=1)
        size_pivot = size_pivot.sort_values('Total', ascending=False).head(15)

        # Chuẩn bị dữ liệu cho stacked bar
        products = size_pivot['Product_Name']
        sizes = ['S', 'M', 'L']

        # Tạo biểu đồ
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # Stacked bar chart
        bottom = np.zeros(len(products))
        colors = {'S': '#FF9AA2', 'M': '#FFB7B2', 'L': '#FFDAC1'}

        for size in sizes:
            values = size_pivot[size]
            ax1.barh(products, values, left=bottom, label=size, color=colors[size])
            bottom += values

        ax1.set_xlabel('Số lượng', fontsize=12)
        ax1.set_ylabel('Sản phẩm', fontsize=12)
        ax1.set_title('Phân bổ kích cỡ sản phẩm (L/M/S)', fontsize=14, fontweight='bold')
        ax1.legend(title='Kích cỡ')
        ax1.invert_yaxis()

        # Donut chart cho tổng phân phối size
        total_by_size = self.df.groupby('Size')['Quantity'].sum()

        wedges, texts, autotexts = ax2.pie(total_by_size.values, labels=total_by_size.index,
                                           autopct='%1.1f%%', startangle=90,
                                           colors=[colors.get(s, 'gray') for s in total_by_size.index],
                                           pctdistance=0.85)

        # Tạo donut
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax2.add_artist(centre_circle)

        ax2.set_title('Tổng phân phối kích cỡ toàn hệ thống', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/product_size_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ phân bổ kích cỡ: {self.output_dir}/product_size_distribution.png")
        return True

    def create_all_charts(self, top_n=10):
        """Tạo tất cả biểu đồ liên quan đến sản phẩm"""
        print("Đang tạo biểu đồ phân tích sản phẩm...")

        results = []
        results.append(self.plot_product_quantity(top_n))
        results.append(self.plot_product_revenue(top_n))
        results.append(self.plot_size_distribution())

        success_count = sum(results)
        print(f"Đã tạo {success_count}/{len(results)} biểu đồ phân tích sản phẩm")
        return success_count


# Hàm chính cho module này
def main_visualize_product(df_path='output/cleaned_data.csv'):
    """Hàm chính cho visualization sản phẩm"""
    print("=" * 60)
    print("TRỰC QUAN HÓA DỮ LIỆU THEO SẢN PHẨM")
    print("=" * 60)

    if not os.path.exists(df_path):
        print(f"File {df_path} không tồn tại!")
        return False

    # Đọc dữ liệu
    df = pd.read_csv(df_path)
    print(f"Đã tải {len(df)} bản ghi")

    # Khởi tạo visualizer
    visualizer = ProductVisualizer(df)

    # Tạo tất cả biểu đồ
    visualizer.create_all_charts(top_n=10)

    return True


if __name__ == "__main__":
    main_visualize_product()