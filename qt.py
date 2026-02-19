from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import sys
from PyQt6.QtCore import Qt
import math
import time
from toric_simulator import ToricSimulator


class MyWindow(QWidget):
    def __init__(self):
        self.label = "Hello world"
        super().__init__()

        self.empty_edge_color = QColor(150, 150, 150)
        self.half_edge_color = QColor(255, 25, 25)
        self.full_grown_edge = QColor(25, 25, 255)
        self.spanning_tree_edge = QColor(105, 215, 215)
        self.corrected_edge = QColor(155, 55, 25)
        self.syndrome_color = QColor(25, 255, 25)
        self.cluster_color = QColor(255, 100, 255)


    def paintEvent(self, event):
        painter = QPainter(self)

        self.draw_probability(painter)
    
    def set_toric(self, toric):
        self.toric = toric

    def draw_probability(self, painter):
        #figure out radius and line length
        line_length = 450 / self.toric.L
        if (line_length > 50):
            line_length = 50
        radius = line_length / 4

        start_x = 50
        start_y = 50

        for y in range(0, self.toric.L*2, 2):
            for x in range(self.toric.L):
                color = self.empty_edge_color
                if (self.toric.edges[y*self.toric.L + x] == 1):
                    color = self.half_edge_color
                elif (self.toric.edges[y*self.toric.L + x] == 2):
                    color = self.full_grown_edge
                elif (self.toric.edges[y*self.toric.L + x] == 3):
                    color = self.spanning_tree_edge
                elif (self.toric.tree[y*self.toric.L + x] == 4):
                    color = self.corrected_edge
                self.draw_line(painter, color, start_x + x*line_length, start_y + y/2*line_length, start_x + (x+1)*line_length, start_y + y/2*line_length)

            for x in range(self.toric.L):
                color = self.empty_edge_color
                if (self.toric.edges[(y+1)*self.toric.L + x] == 1):
                    color = self.half_edge_color
                elif (self.toric.edges[(y+1)*self.toric.L + x] == 2):
                    color = self.full_grown_edge
                elif (self.toric.edges[(y+1)*self.toric.L + x] == 3):
                    color = self.spanning_tree_edge
                elif (self.toric.tree[(y+1)*self.toric.L + x] == 4):
                    color = self.corrected_edge
                self.draw_line(painter, color, start_x + x*line_length, start_y + (y/2)*line_length, start_x + x*line_length, start_y + (y/2+1)*line_length)
        
        for y in range(0, self.toric.L*2, 2):
            for x in range(self.toric.L):
                color = QColor(100, 100, 100)
                vertex = int(y/2)*self.toric.L + x
                if (self.toric.display_syndrome[vertex] == 1):
                    color = QColor(25, 255, 25)
                elif (self.toric.parent[vertex] != vertex):
                    color = QColor(255, 100, 255)
                self.draw_dot(painter, color, start_x + x*line_length, start_y + y/2*line_length, radius)
        
        #Draw instructions
        font = QFont("Arial", 20)
        legend_x = 550
        painter.setFont(font)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(legend_x, 70, "Legend:")
        color = self.empty_edge_color
        self.draw_line(painter, color, legend_x, 95, legend_x+30, 95)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 105, "Empty edge")
        color = self.half_edge_color
        self.draw_line(painter, color, legend_x, 130, legend_x+30, 130)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 140, "Half-grown edge")
        color = self.full_grown_edge
        self.draw_line(painter, color, legend_x, 165, legend_x+30, 165)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 175, "Full-grown edge")
        color = self.spanning_tree_edge
        self.draw_line(painter, color, legend_x, 200, legend_x+30, 200)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 210, "Spanning-tree edge")
        color = self.corrected_edge
        self.draw_line(painter, color, legend_x, 235, legend_x+30, 235)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 245, "Solution edge")
        color = self.cluster_color
        self.draw_dot(painter, color, legend_x+15, 270, radius)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 280, "Cluster vertex")
        color = self.syndrome_color
        self.draw_dot(painter, color, legend_x+15, 305, radius)
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 315, "Syndrome vertex")


        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 360, "Controls:")
        painter.drawText(600, 385, "W/S: +/- lattice size")
        painter.drawText(600, 410, "A/D: +/- error rate")
        if (self.toric.has_odd()):
            painter.setPen(QColor(50, 50, 50))  # RGB color
        else:
            painter.setPen(QColor(150, 150, 150))  # RGB color
        painter.drawText(600, 435, "T: Grow clusters")
        if (not self.toric.has_odd()):
            painter.setPen(QColor(50, 50, 50))  # RGB color
        else:
            painter.setPen(QColor(150, 150, 150))  # RGB color
        painter.drawText(600, 460, "F: Peel clusters")
        painter.setPen(QColor(50, 50, 50))  # RGB color
        painter.drawText(600, 485, f"Error rate: {self.toric.error_rate:.3}")
        
                
    
    def draw_line(self, painter, color, x, y, x1, y1):
        pen = QPen(color)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawLine(int(x), int(y), int(x1), int(y1))
    
    def draw_dot(self, painter, color, x, y, radius):
        painter.setBrush(color)
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(int(x-radius/3), int(y-radius/3), int(radius), int(radius))
