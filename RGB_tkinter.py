import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


def calculate_rgb_average():
    # 打开文件选择对话框
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename()

    # 读取图像
    image = cv2.imread(image_path)
    # 获取原始图像的宽度和高度
    original_height, original_width = image.shape[:2]

    # 计算缩放比例
    scale_ratio = 1280 / float(original_width)
    target_width = 1280
    target_height = int(original_height * scale_ratio)

    # 缩放图像
    image = cv2.resize(image, (target_width, target_height))

    # 创建窗口并设置鼠标事件回调函数
    cv2.namedWindow("Select Region")
    cv2.setMouseCallback("Select Region", select_region_callback)

    # 显示图像，等待用户选择区域
    selected_region = cv2.selectROI(
        "Select Region", image, fromCenter=False, showCrosshair=True
    )

    # 获取选定区域的像素数据
    region_pixels = image[
        int(selected_region[1]) : int(selected_region[1] + selected_region[3]),
        int(selected_region[0]) : int(selected_region[0] + selected_region[2]),
    ]

    # 计算RGB均值
    avg_rgb = cv2.mean(region_pixels)[:3]
    avg_rgb = [avg_rgb[2], avg_rgb[1], avg_rgb[0]]  # 将B和R通道的值交换位置得到RGB顺序的结果

    # 关闭窗口
    cv2.destroyAllWindows()

    return avg_rgb, region_pixels


# 鼠标事件回调函数，用于处理用户选择区域
def select_region_callback(event, x, y, flags, param):
    global selected_region
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_region = (x, y, 0, 0)  # 初始化选定区域的坐标
    elif event == cv2.EVENT_LBUTTONUP:
        selected_region = (
            selected_region[0],
            selected_region[1],
            x - selected_region[0],
            y - selected_region[1],
        )
        # 在图像上绘制选定区域的矩形框
        cv2.rectangle(
            image, (selected_region[0], selected_region[1]), (x, y), (0, 255, 0), 2
        )
        cv2.imshow("Select Region", image)


# 创建图形界面
def create_gui():
    global result_label, image_label

    # 创建主窗口
    root = tk.Tk()
    root.title("RGB Average Calculator")
    root.geometry("1280x720")  # 设置窗口大小为1280x720像素

    # 创建选择图像按钮
    button = tk.Button(
        root,
        text="Select Image",
        command=lambda: calculate_and_update_rgb_average(result_label, image_label),
    )
    button.pack(pady=10)

    # 创建用于显示结果的Label组件
    result_label = tk.Label(root, text="RGB Average: ")
    result_label.pack(pady=10)

    # 创建用于显示选定区域图像的Label组件
    image_label = tk.Label(root)
    image_label.pack(pady=10)

    # 启动图形界面的消息循环
    root.mainloop()


# 将结果显示在Label组件中，并显示选定区域图像
def calculate_and_update_rgb_average(result_label, image_label):
    avg_rgb, region_pixels = calculate_rgb_average()
    result_label.config(text="RGB Average: {}".format(avg_rgb))

    # 将选定区域图像显示在GUI上
    region_pixels_rgb = cv2.cvtColor(region_pixels, cv2.COLOR_BGR2RGB)
    region_image = Image.fromarray(region_pixels_rgb)
    region_image = region_image.resize((640, 360))  # 缩放选定区域图像至固定大小
    region_photo = ImageTk.PhotoImage(region_image)
    image_label.config(image=region_photo)
    image_label.image = region_photo


# 示例用法
create_gui()
