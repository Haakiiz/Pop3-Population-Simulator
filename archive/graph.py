import matplotlib.pyplot as plt

#burde importere 123 fila... og få inn population og time_list datasetta

graph_population = [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8, 11, 12, 12, 12, 17, 18, 18, 18, 18, 18, 21, 21, 27, 30, 35, 36, 36, 45, 50, 62, 64, 69, 74, 82, 88, 95, 108, 119, 130, 142, 164, 180, 207, 223, 246, 274]
graph_time = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490]

# population = population[:len(time_list)]

# print(population)
# print(time_list)


plt.plot(graph_time, graph_population)
plt.xlabel('Time')
plt.ylabel('Population')
plt.title('Population over Time')
plt.show()