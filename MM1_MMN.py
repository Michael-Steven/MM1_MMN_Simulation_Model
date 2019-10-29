import random
import numpy as npy
import math


class MM1:
    def __init__(self, arrive_time, serve_time, num, length):
        self.average_arrive_time = arrive_time
        self.average_serve_time = serve_time
        self.custom_num = num
        self.max_length = length
        self.arrive_space = []  # 到达时间间隔（泊松分布）
        self.arrive_time = []  # 到达时间
        self.serve_time = []  # 服务时间（指数分布）
        self.leave_time = []  # 离开时间（由到达时间和服务时间计算出）
        self.queue_time = []  # 排队时间（从到达到接受服务）
        self.wait_time = []  # 等待时间（从来到走）

    def produce(self):
        # 生成服从泊松分布的到达时间间隔
        poisson = npy.random.poisson(self.average_arrive_time, self.custom_num)
        for i in range(0, self.custom_num):
            disturb = random.uniform(-0.5, 0.5)
            self.arrive_space.append(poisson[i] + disturb)
        # ans = 0
        # print("[", end='')
        # for i in range(0, self.custom_num):
        #     ans = ans + self.arrive_space[i]
        #     print("%f, " % self.arrive_space[i], end='')
        # print("]")
        # ans = ans / self.custom_num
        # print(ans)
        # 计算到达时间
        self.arrive_time.append(self.arrive_space[0])
        for i in range(1, self.custom_num):
            self.arrive_time.append(self.arrive_time[i - 1] + self.arrive_space[i])
        # print(self.arrive_time)
        # print(len(self.arrive_time))

    def leave(self):
        # 生成服从指数分布的服务时间
        for i in range(0, self.custom_num):
            ran = -self.average_serve_time * math.log(random.uniform(0, 1))
            self.serve_time.append(ran)
        # ans1 = 0
        # print("[", end='')
        # for i in range(0, self.custom_num):
        #     ans1 = ans1 + self.serve_time[i]
        #     print("%f, " % self.serve_time[i], end='')
        # print("]")
        # ans1 = ans1 / self.custom_num
        # print(len(self.serve_time))
        # print(ans1)
        self.leave_time.append(self.serve_time[0] + self.arrive_time[0])
        i = 1
        while i < self.custom_num:
            # 新来人时统计队伍里人数，人满了就不排队了
            cnt = 0
            for j in range(0, i):
                if self.arrive_time[j] <= self.arrive_time[i] <= self.leave_time[j]:
                    cnt = cnt + 1
            if cnt >= self.max_length:
                self.arrive_time.remove(self.arrive_time[i])
                self.serve_time.remove(self.serve_time[i])
                self.custom_num = self.custom_num - 1
                continue
            # 离开时间的计算方法：
            # 如果前面那个人的离开时间大于我，我的离开时间等于他的离开时间加上我的服务时间
            # 如果前面那个人的离开时间小于我，我的离开时间等于我的到达时间加上我的服务时间
            if self.leave_time[i - 1] < self.arrive_time[i]:
                self.leave_time.append(self.arrive_time[i] + self.serve_time[i])
            else:
                self.leave_time.append(self.leave_time[i - 1] + self.serve_time[i])
            i = i + 1
        # 计算排队时间和等待时间
        for i in range(0, self.custom_num):
            self.queue_time.append(self.leave_time[i] - self.arrive_time[i])
        # print(self.arrive_time)
        # print(self.leave_time)
        # print(self.serve_time)
        # print(self.queue_time)
        # print(self.custom_num)
        # print(len(self.arrive_time))
        # print(len(self.leave_time))
        # print(len(self.serve_time))

    def simulate(self):
        print("average delay in the queue : ")
        print("%f" % (sum(self.queue_time) / self.custom_num))
        print("average customs number in the queue : ")
        print("%f" % (sum(self.queue_time) / self.leave_time[self.custom_num - 1]))
        print("utilisation of server : ")
        print("%f" % (sum(self.serve_time) / self.leave_time[self.custom_num - 1]))


class MMN(MM1):
    def __init__(self, arrive_time, serve_time, num, length, window_num):
        MM1.__init__(self, arrive_time, serve_time, num, length)
        self.window_num = window_num
        self.leave_x = []
        self.queue_x = []
        self.serve_x = []

    def leave(self):
        # 生成服从指数分布的服务时间
        for i in range(0, self.custom_num):
            ran = -self.average_serve_time * math.log(random.uniform(0, 1))
            self.serve_time.append(ran)
        # ans1 = 0
        # print("[", end='')
        # for i in range(0, self.custom_num):
        #     ans1 = ans1 + self.serve_time[i]
        #     print("%f, " % self.serve_time[i], end='')
        # print("]")
        # ans1 = ans1 / self.custom_num
        # print(len(self.serve_time))
        # print(ans1)
        # 先给每个窗口分一个顾客
        for i in range(0, self.window_num):
            self.leave_time.append(self.serve_time[i] + self.arrive_time[i])
            self.leave_x.append(self.leave_time[i])
            self.queue_x.append(self.leave_time[i] - self.arrive_time[i])
            self.serve_x.append(self.serve_time[i])
        i = self.window_num
        while i < self.custom_num:
            # 新来人时统计队伍里人数，人满了就不排队了
            cnt = 0
            for j in range(0, i):
                if self.arrive_time[j] <= self.arrive_time[i] <= self.leave_time[j]:
                    cnt = cnt + 1
            if cnt >= self.max_length * self.window_num:
                self.arrive_time.remove(self.arrive_time[i])
                self.serve_time.remove(self.serve_time[i])
                self.custom_num = self.custom_num - 1
                continue
            # 把顾客安排在最早结束的窗口
            earliest = 0
            early_time = 1000000
            for j in range(0, self.window_num):
                if self.leave_x[j] < early_time:
                    early_time = self.leave_x[j]
                    earliest = j
            if self.arrive_time[i] > self.leave_x[earliest]:
                self.leave_time.append(self.arrive_time[i] + self.serve_time[i])
                self.leave_x[earliest] = self.leave_time[i]
            else:
                self.leave_time.append(self.leave_x[earliest] + self.serve_time[i])
                self.leave_x[earliest] = self.leave_time[i]
            self.queue_x[earliest] = self.queue_x[earliest] + self.leave_time[i] - self.arrive_time[i]
            self.serve_x[earliest] = self.serve_x[earliest] + self.serve_time[i]
            i = i + 1
        # 计算排队时间和等待时间
        for i in range(0, self.custom_num):
            self.queue_time.append(self.leave_time[i] - self.arrive_time[i])
        # print(self.arrive_time)
        # print(self.leave_time)
        # print(self.serve_time)
        # print(self.queue_time)
        # print(self.custom_num)
        # print(len(self.arrive_time))
        # print(len(self.leave_time))
        # print(len(self.serve_time))

    def simulate(self):
        print("average delay in the queue : ")
        print("%f" % (sum(self.queue_time) / self.custom_num))
        print("average customs number in the queue : ")
        for i in range(0, self.window_num):
            print("  queue %d : " % (i + 1), end='')
            print("%f" % (self.queue_x[i] / self.leave_x[i]))
        print("utilisation of server : ")
        for i in range(0, self.window_num):
            print("  queue %d : " % (i + 1), end='')
            print("%f" % (self.serve_x[i] / self.leave_x[i]))


def main():
    print("average arrive space time : ")
    arrive_time = int(input())
    print("average serve time : ")
    serve_time = int(input())
    print("number of customs : ")
    num = int(input())
    print("max length of queue : ")
    length = int(input())
    print("MMN window number : ")
    window_num = int(input())
    print("\nMM1 result : ")
    t = MM1(arrive_time, serve_time, num, length)
    t.produce()
    t.leave()
    t.simulate()
    print("\nMMN result : ")
    tn = MMN(arrive_time, serve_time, num, length, window_num)
    tn.produce()
    tn.leave()
    tn.simulate()


if __name__ == '__main__':
    main()
