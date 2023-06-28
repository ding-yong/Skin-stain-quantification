from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QLabel,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
import cv2
from PIL import Image


class RGBAverageCalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RGB Average Calculator")
        self.setGeometry(100, 100, 1280, 720)

        self.button = QPushButton("Select Image", self)
        self.button.setGeometry(10, 10, 150, 50)
        self.button.clicked.connect(self.calculate_and_update_rgb_average)

        self.result_label = QLineEdit("RGB Average:", self)
        self.result_label.setReadOnly(True)
        self.result_label.setGeometry(10, 70, 150, 30)

        self.image_label = QLabel(self)
        self.image_label.setGeometry(170, 10, 640, 360)
        self.image_label.setAlignment(Qt.AlignCenter)

    def calculate_rgb_average(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.bmp)")
        if file_dialog.exec_():
            image_path = file_dialog.selectedFiles()[0]

            image = cv2.imread(image_path)
            original_height, original_width = image.shape[:2]

            scale_ratio = 1280 / float(original_width)
            target_width = 1280
            target_height = int(original_height * scale_ratio)

            image = cv2.resize(image, (target_width, target_height))

            cv2.namedWindow("Select Region")
            cv2.setMouseCallback("Select Region", self.select_region_callback)

            selected_region = cv2.selectROI(
                "Select Region", image, fromCenter=False, showCrosshair=True
            )

            region_pixels = image[
                int(selected_region[1]) : int(selected_region[1] + selected_region[3]),
                int(selected_region[0]) : int(selected_region[0] + selected_region[2]),
            ]

            avg_rgb = cv2.mean(region_pixels)[:3]
            avg_rgb = [avg_rgb[2], avg_rgb[1], avg_rgb[0]]

            cv2.destroyAllWindows()

            return avg_rgb, region_pixels

    def select_region_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_region = (x, y, 0, 0)
        elif event == cv2.EVENT_LBUTTONUP:
            self.selected_region = (
                self.selected_region[0],
                self.selected_region[1],
                x - self.selected_region[0],
                y - self.selected_region[1],
            )
            cv2.rectangle(
                self.image,
                (self.selected_region[0], self.selected_region[1]),
                (x, y),
                (0, 255, 0),
                2,
            )
            cv2.imshow("Select Region", self.image)

    def calculate_and_update_rgb_average(self):
        avg_rgb, region_pixels = self.calculate_rgb_average()
        self.result_label.setText("RGB Average: {}".format(avg_rgb))

        # 将选定区域图像显示在GUI上
        region_pixels_rgb = cv2.cvtColor(region_pixels, cv2.COLOR_BGR2RGB)
        region_image = Image.fromarray(region_pixels_rgb)
        region_image = region_image.resize((640, 360))  # 缩放选定区域图像至固定大小

        # 转换为QImage格式
        qimage = QImage(
            region_image.tobytes(),
            region_image.width,
            region_image.height,
            QImage.Format_RGB888,
        )

        # 创建QPixmap并设置给image_label
        qpixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(qpixmap)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = RGBAverageCalculatorWindow()
    window.show()
    sys.exit(app.exec_())
