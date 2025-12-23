"""visualize_channel.py - Biểu đồ phân tích theo kênh bán hàng"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


class ChannelVisualizer:
    def __init__(self, df):
        self.df = df
        self.output_dir = 'output/charts'
        os.makedirs(self.output_dir, exist_ok=True)

        # Thiết lập style
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_channel_revenue(self, figsize=(12, 10)):
        """Biểu đồ doanh thu theo kênh"""
        if 'Order_Channel' not in self.df.columns or 'Revenue' not in self.df.columns:
            print(" Thiếu cột Order_Channel hoặc Revenue!")
            return False

        # Tính toán dữ liệu
        channel_data = self.df.groupby('Order_Channel').agg({
            'Revenue': 'sum',
            'Quantity': 'sum',
            'Sale_id': 'count'  # Số đơn hàng
        }).reset_index()

        channel_data = channel_data.rename(columns={'Sale_id': 'Order_Count'})
        channel_data = channel_data.sort_values('Revenue', ascending=False)

        # Tạo biểu đồ
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        # 1. Pie chart - Phân phối doanh thu
        colors = sns.color_palette("Set2", len(channel_data))
        wedges, texts, autotexts = ax1.pie(channel_data['Revenue'],
                                           labels=channel_data['Order_Channel'],
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           colors=colors,
                                           explode=[0.05] * len(channel_data))

        ax1.set_title('Phân phối doanh thu theo kênh', fontsize=14, fontweight='bold')

        # Cải thiện hiển thị phần trăm
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        # 2. Bar chart - Doanh thu
        bars = ax2.bar(channel_data['Order_Channel'], channel_data['Revenue'] / 1e6,
                       color=colors)
        ax2.set_xlabel('Kênh bán hàng', fontsize=12)
        ax2.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax2.set_title('Doanh thu theo kênh', fontsize=14, fontweight='bold')
        ax2.set_xticklabels(channel_data['Order_Channel'].tolist(), rotation=0)
        ax2.grid(True, alpha=0.3, axis='y')

        # Thêm giá trị trên cột
        for bar, revenue in zip(bars, channel_data['Revenue'] / 1e6):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{revenue:,.1f}', ha='center', va='bottom', fontsize=10)

        # 3. Bar chart - Số lượng đơn hàng
        bars = ax3.bar(channel_data['Order_Channel'], channel_data['Order_Count'],
                       color=colors)
        ax3.set_xlabel('Kênh bán hàng', fontsize=12)
        ax3.set_ylabel('Số đơn hàng', fontsize=12)
        ax3.set_title('Số lượng đơn hàng theo kênh', fontsize=14, fontweight='bold')
        ax3.set_xticklabels(channel_data['Order_Channel'].tolist(), rotation=45)
        ax3.grid(True, alpha=0.3, axis='y')

        # Thêm giá trị trên cột
        for bar, count in zip(bars, channel_data['Order_Count']):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{count:,}', ha='center', va='bottom', fontsize=10)

        # 4. Scatter plot - Mối quan hệ Số đơn vs Doanh thu
        scatter = ax4.scatter(channel_data['Order_Count'], channel_data['Revenue'] / 1e6,
                              s=channel_data['Quantity'] / 10,  # Kích thước theo số lượng
                              c=range(len(channel_data)),
                              cmap='viridis', alpha=0.8, edgecolors='black')

        ax4.set_xlabel('Số đơn hàng', fontsize=12)
        ax4.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax4.set_title('Mối quan hệ Số đơn - Doanh thu', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        # Thêm label cho mỗi điểm
        for i, row in channel_data.iterrows():
            ax4.annotate(row['Order_Channel'],
                         (row['Order_Count'], row['Revenue'] / 1e6),
                         xytext=(5, 5), textcoords='offset points',
                         fontsize=9)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/channel_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ phân tích kênh: {self.output_dir}/channel_analysis.png")
        return True

    def plot_channel_trend(self, figsize=(14, 8)):
        """Biểu đồ xu hướng kênh theo thời gian"""
        if not all(col in self.df.columns for col in ['Order_Channel', 'Year_Month', 'Revenue']):
            print(" Thiếu cột cần thiết!")
            return False

        # Tính toán dữ liệu
        trend_data = self.df.groupby(['Year_Month', 'Order_Channel']).agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        }).reset_index()

        # Pivot cho biểu đồ
        revenue_pivot = trend_data.pivot(index='Year_Month',
                                         columns='Order_Channel',
                                         values='Revenue').fillna(0)

        quantity_pivot = trend_data.pivot(index='Year_Month',
                                          columns='Order_Channel',
                                          values='Quantity').fillna(0)

        # Tạo biểu đồ
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # 1. Line chart - Doanh thu theo thời gian
        for channel in revenue_pivot.columns:
            ax1.plot(revenue_pivot.index, revenue_pivot[channel] / 1e6,
                     marker='o', linewidth=2, markersize=5, label=channel)

        ax1.set_xlabel('Tháng', fontsize=12)
        ax1.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax1.set_title('Xu hướng doanh thu theo kênh', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticklabels(revenue_pivot.index, rotation=45)

        # 2. Stacked area chart - Phân phối theo thời gian
        colors = sns.color_palette("Set2", len(revenue_pivot.columns))

        ax2.stackplot(revenue_pivot.index,
                      [revenue_pivot[col] / 1e6 for col in revenue_pivot.columns],
                      labels=revenue_pivot.columns,
                      colors=colors, alpha=0.8)

        ax2.set_xlabel('Tháng', fontsize=12)
        ax2.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax2.set_title('Phân phối doanh thu theo thời gian', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticklabels(revenue_pivot.index, rotation=45)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/channel_trend.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f" Đã lưu biểu đồ xu hướng kênh: {self.output_dir}/channel_trend.png")
        return True

    def plot_channel_by_product(self, top_n_products=5, figsize=(12, 8)):
        """Biểu đồ kênh phân phối theo sản phẩm"""
        if not all(col in self.df.columns for col in ['Order_Channel', 'Product_Name', 'Revenue']):
            print(" Thiếu cột cần thiết!")
            return False

        # Lấy top N sản phẩm
        top_products = self.df.groupby('Product_Name')['Revenue'].sum() \
            .nlargest(top_n_products).index.tolist()

        # Lọc dữ liệu cho top sản phẩm
        product_data = self.df[self.df['Product_Name'].isin(top_products)]

        # Tạo pivot table
        product_channel_pivot = product_data.pivot_table(
            index='Product_Name',
            columns='Order_Channel',
            values='Revenue',
            aggfunc='sum',
            fill_value=0
        )

        # Tạo biểu đồ
        fig, ax = plt.subplots(figsize=figsize)

        x = range(len(product_channel_pivot))
        width = 0.35
        channels = product_channel_pivot.columns

        if len(channels) >= 2:
            # Grouped bar chart
            for i, channel in enumerate(channels):
                offset = (i - (len(channels) - 1) / 2) * width
                bars = ax.bar([pos + offset for pos in x],
                              product_channel_pivot[channel] / 1e6,
                              width, label=channel)

                # Thêm giá trị trên cột
                for bar, value in zip(bars, product_channel_pivot[channel] / 1e6):
                    if value > 0:
                        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height(),
                                f'{value:,.1f}', ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Sản phẩm', fontsize=12)
        ax.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax.set_title(f'Phân phối kênh cho top {top_n_products} sản phẩm',
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(product_channel_pivot.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/channel_by_product.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f" Đã lưu biểu đồ kênh theo sản phẩm: {self.output_dir}/channel_by_product.png")
        return True

    def create_all_charts(self):
        """Tạo tất cả biểu đồ liên quan đến kênh bán hàng"""
        print(" Đang tạo biểu đồ phân tích kênh bán hàng...")

        results = []
        results.append(self.plot_channel_revenue())
        results.append(self.plot_channel_trend())
        results.append(self.plot_channel_by_product())

        success_count = sum(results)
        print(f" Đã tạo {success_count}/{len(results)} biểu đồ phân tích kênh")
        return success_count


# Hàm chính cho module này
def main_visualize_channel(df_path='output/cleaned_data.csv'):
    """Hàm chính cho visualization kênh bán hàng"""
    print("=" * 60)
    print("TRỰC QUAN HÓA DỮ LIỆU THEO KÊNH BÁN HÀNG")
    print("=" * 60)

    if not os.path.exists(df_path):
        print(f" File {df_path} không tồn tại!")
        return False

    # Đọc dữ liệu
    df = pd.read_csv(df_path)
    print(f"Đã tải {len(df)} bản ghi")

    # Khởi tạo visualizer
    visualizer = ChannelVisualizer(df)

    # Tạo tất cả biểu đồ
    visualizer.create_all_charts()

    return True


if __name__ == "__main__":
    main_visualize_channel()