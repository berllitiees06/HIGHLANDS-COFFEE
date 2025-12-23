"""visualize_staff.py - Biểu đồ phân tích theo nhân viên"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


class StaffVisualizer:
    def __init__(self, df):
        self.df = df
        self.output_dir = 'output/charts'
        os.makedirs(self.output_dir, exist_ok=True)

        # Thiết lập style
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_top_staff(self, top_n=15, figsize=(14, 10)):
        """Biểu đồ top nhân viên xuất sắc"""
        if 'Staff_id' not in self.df.columns or 'Revenue' not in self.df.columns:
            print("Thiếu cột Staff_id hoặc Revenue!")
            return False

        # Tính toán dữ liệu
        staff_data = self.df.groupby('Staff_id').agg({
            'Revenue': 'sum',
            'Quantity': 'sum',
            'Sale_id': 'count'  # Số đơn hàng
        }).reset_index()

        staff_data = staff_data.rename(columns={'Sale_id': 'Order_Count'})
        staff_data = staff_data.sort_values('Revenue', ascending=False)

        # Lấy top N nhân viên
        top_staff = staff_data.head(top_n)

        # Tạo biểu đồ
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        # 1. Horizontal bar chart - Top nhân viên
        bars = ax1.barh(top_staff['Staff_id'], top_staff['Revenue'] / 1e6,
                        color=sns.color_palette("Blues_r", top_n))
        ax1.set_xlabel('Doanh thu (triệu VND)', fontsize=12)
        ax1.set_ylabel('Mã nhân viên', fontsize=12)
        ax1.set_title(f'Top {top_n} nhân viên doanh thu cao nhất',
                      fontsize=14, fontweight='bold')
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3, axis='x')

        # Thêm giá trị trên cột
        for bar, revenue in zip(bars, top_staff['Revenue'] / 1e6):
            ax1.text(revenue + 0.1, bar.get_y() + bar.get_height() / 2,
                     f'{revenue:,.1f}', va='center', fontsize=10)

        # 2. Scatter plot - Mối quan hệ Số đơn vs Doanh thu
        scatter = ax2.scatter(staff_data['Order_Count'], staff_data['Revenue'] / 1e6,
                              s=staff_data['Quantity'] / 5,  # Kích thước theo số lượng
                              c=range(len(staff_data)),
                              cmap='viridis', alpha=0.7, edgecolors='black')

        ax2.set_xlabel('Số đơn hàng', fontsize=12)
        ax2.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax2.set_title('Mối quan hệ Số đơn - Doanh thu', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Đánh dấu top 3
        top3 = staff_data.head(3)
        for _, row in top3.iterrows():
            ax2.annotate(row['Staff_id'],
                         (row['Order_Count'], row['Revenue'] / 1e6),
                         xytext=(10, 5), textcoords='offset points',
                         fontsize=10, fontweight='bold',
                         arrowprops=dict(arrowstyle='->', color='red'))

        # 3. Bar chart - Số lượng đơn hàng
        bars = ax3.bar(top_staff['Staff_id'], top_staff['Order_Count'],
                       color=sns.color_palette("Greens_r", top_n))
        ax3.set_xlabel('Mã nhân viên', fontsize=12)
        ax3.set_ylabel('Số đơn hàng', fontsize=12)
        ax3.set_title(f'Số đơn hàng top {top_n} nhân viên',
                      fontsize=14, fontweight='bold')
        ax3.set_xticklabels(top_staff['Staff_id'], rotation=45, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')

        # Thêm giá trị trên cột
        for bar, count in zip(bars, top_staff['Order_Count']):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{count}', ha='center', va='bottom', fontsize=9)

        # 4. Histogram - Phân phối doanh thu
        ax4.hist(staff_data['Revenue'] / 1e6, bins=20,
                 color='skyblue', edgecolor='black', alpha=0.7)
        ax4.set_xlabel('Doanh thu (triệu VND)', fontsize=12)
        ax4.set_ylabel('Số nhân viên', fontsize=12)
        ax4.set_title('Phân phối doanh thu nhân viên', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        # Thêm đường trung bình
        mean_revenue = staff_data['Revenue'].mean() / 1e6
        ax4.axvline(mean_revenue, color='red', linestyle='--', linewidth=2,
                    label=f'Trung bình: {mean_revenue:.1f} triệu')
        ax4.legend()

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/top_staff_performance.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ top nhân viên: {self.output_dir}/top_staff_performance.png")
        return True

    def plot_staff_by_channel(self, top_n_staff=10, figsize=(12, 8)):
        """Biểu đồ phân tích nhân viên theo kênh"""
        if not all(col in self.df.columns for col in ['Staff_id', 'Order_Channel', 'Revenue']):
            print("Thiếu cột cần thiết!")
            return False

        # Lấy top N nhân viên
        top_staff_ids = self.df.groupby('Staff_id')['Revenue'].sum() \
            .nlargest(top_n_staff).index.tolist()

        # Lọc dữ liệu cho top nhân viên
        staff_data = self.df[self.df['Staff_id'].isin(top_staff_ids)]

        # Tạo pivot table
        staff_channel_pivot = staff_data.pivot_table(
            index='Staff_id',
            columns='Order_Channel',
            values='Revenue',
            aggfunc='sum',
            fill_value=0
        )

        # Tạo biểu đồ
        fig, ax = plt.subplots(figsize=figsize)

        # Stacked bar chart
        channels = staff_channel_pivot.columns
        colors = sns.color_palette("Set2", len(channels))

        bottom = None
        for i, channel in enumerate(channels):
            if bottom is None:
                bars = ax.bar(staff_channel_pivot.index,
                              staff_channel_pivot[channel] / 1e6,
                              label=channel, color=colors[i])
                bottom = staff_channel_pivot[channel].values
            else:
                bars = ax.bar(staff_channel_pivot.index,
                              staff_channel_pivot[channel] / 1e6,
                              bottom=bottom, label=channel, color=colors[i])
                bottom += staff_channel_pivot[channel].values

        ax.set_xlabel('Mã nhân viên', fontsize=12)
        ax.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax.set_title(f'Phân phối kênh cho top {top_n_staff} nhân viên',
                     fontsize=14, fontweight='bold')
        ax.set_xticklabels(staff_channel_pivot.index, rotation=45, ha='right')
        ax.legend(title='Kênh bán')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/staff_by_channel.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ nhân viên theo kênh: {self.output_dir}/staff_by_channel.png")
        return True

    def plot_staff_trend(self, top_n_staff=5, figsize=(14, 8)):
        """Biểu đồ xu hướng nhân viên theo thời gian"""
        if not all(col in self.df.columns for col in ['Staff_id', 'Year_Month', 'Revenue']):
            print("Thiếu cột cần thiết!")
            return False

        # Lấy top N nhân viên
        top_staff_ids = self.df.groupby('Staff_id')['Revenue'].sum() \
            .nlargest(top_n_staff).index.tolist()

        # Lọc dữ liệu
        trend_data = self.df[self.df['Staff_id'].isin(top_staff_ids)]
        trend_data = trend_data.groupby(['Year_Month', 'Staff_id'])['Revenue'].sum().reset_index()

        # Pivot table
        trend_pivot = trend_data.pivot(index='Year_Month',
                                       columns='Staff_id',
                                       values='Revenue').fillna(0)

        # Tạo biểu đồ
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # 1. Line chart - Xu hướng
        colors = sns.color_palette("husl", len(top_staff_ids))
        for i, staff_id in enumerate(top_staff_ids):
            if staff_id in trend_pivot.columns:
                ax1.plot(trend_pivot.index, trend_pivot[staff_id] / 1e6,
                         marker='o', linewidth=2, markersize=4,
                         color=colors[i], label=staff_id)

        ax1.set_xlabel('Tháng', fontsize=12)
        ax1.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax1.set_title(f'Xu hướng doanh thu top {top_n_staff} nhân viên',
                      fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticklabels(trend_pivot.index, rotation=45)

        # 2. Heatmap - Hiệu suất theo tháng
        heatmap_data = trend_pivot / 1e6  # Chuyển sang triệu VND

        im = ax2.imshow(heatmap_data.T, aspect='auto', cmap='YlOrRd')
        ax2.set_xlabel('Tháng', fontsize=12)
        ax2.set_ylabel('Nhân viên', fontsize=12)
        ax2.set_title(f'Hiệu suất nhân viên theo tháng (triệu VND)',
                      fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(heatmap_data.index)))
        ax2.set_xticklabels(heatmap_data.index, rotation=45)
        ax2.set_yticks(range(len(heatmap_data.columns)))
        ax2.set_yticklabels(heatmap_data.columns)

        # Thêm giá trị vào heatmap
        for i in range(len(heatmap_data.columns)):
            for j in range(len(heatmap_data.index)):
                value = heatmap_data.iloc[j, i]
                if value > 0:
                    ax2.text(j, i, f'{value:.1f}',
                             ha='center', va='center',
                             color='black' if value < heatmap_data.values.max() / 2 else 'white',
                             fontsize=8)

        plt.colorbar(im, ax=ax2)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/staff_trend.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ xu hướng nhân viên: {self.output_dir}/staff_trend.png")
        return True

    def create_all_charts(self, top_n=15):
        """Tạo tất cả biểu đồ liên quan đến nhân viên"""
        print("\n👥 Đang tạo biểu đồ phân tích nhân viên...")

        results = []
        results.append(self.plot_top_staff(top_n))
        results.append(self.plot_staff_by_channel(min(10, top_n)))
        results.append(self.plot_staff_trend(min(5, top_n)))

        success_count = sum(results)
        print(f"Đã tạo {success_count}/{len(results)} biểu đồ phân tích nhân viên")
        return success_count


# Hàm chính cho module này
def main_visualize_staff(df_path='output/cleaned_data.csv'):
    """Hàm chính cho visualization nhân viên"""
    print("=" * 60)
    print("TRỰC QUAN HÓA DỮ LIỆU THEO NHÂN VIÊN")
    print("=" * 60)

    if not os.path.exists(df_path):
        print(f"File {df_path} không tồn tại!")
        return False

    # Đọc dữ liệu
    df = pd.read_csv(df_path)
    print(f"📁 Đã tải {len(df)} bản ghi")

    # Khởi tạo visualizer
    visualizer = StaffVisualizer(df)

    # Tạo tất cả biểu đồ
    visualizer.create_all_charts(top_n=15)

    return True


if __name__ == "__main__":
    main_visualize_staff()