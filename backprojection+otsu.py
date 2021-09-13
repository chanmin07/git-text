import cv2 as cv
import numpy as np
import math
#Labeking 교재 74페이지
# 모델 이미지와 HSV공간으로 변환한 모델 이미지
roi = cv.imread('model.png')
hsv_roi = cv.cvtColor(roi,cv.COLOR_BGR2HSV)

# 타겟 이미지와 HSV공간으로 변환한 타겟 이미지
target = cv.imread('4.jpg')
hsv_target = cv.cvtColor(target,cv.COLOR_BGR2HSV)
# 책에서 q단계로 줄인 2차원 히스토그램을 만든다. 여기서는 64를 사용하였다.
scale = 16

# 각각 q단계인 모델 HS히스토그램과 타겟 HS히스토그램을 만듬
model_hist = np.zeros((scale,scale))
# target_hist = np.zeros((scale,scale))

# 알고리즘 2-2를 사용하여 정규화된 히스토그램을 만든다.(모델만 만듬.)
for i in range(hsv_roi.shape[1]):
    for j in range(hsv_roi.shape[0]):
        model_hist[math.trunc(hsv_roi.item(j,i,0)/180*(scale-1)),math.trunc(hsv_roi.item(j,i,1)*(scale-1)/255)]+=1
for i in range(scale):
    for j in range(scale):
        norm_model_hist = model_hist/(hsv_roi.shape[0] * hsv_roi.shape[1])
norm_model_hist /= np.max(norm_model_hist) # 0~1 사이의 값으로 정규화.

# 타겟이미지와 같은 크기를 가지는 빈 이미지를 만든다.
backP_img = np.zeros((target.shape[0],target.shape[1]),np.float64)
backP_img_u = np.zeros((target.shape[0],target.shape[1]),np.uint8)

# 타겟 이미지의 픽셀값을 양자화 하여 모델 히스토그램으로 이동하여 나오는 색상값으로 역투영을 수행한다.
for i in range(hsv_target.shape[1]):
    for j in range(hsv_target.shape[0]):
        backP_img[j,i] = norm_model_hist[math.trunc(hsv_target.item(j,i,0)/180*(scale-1)),math.trunc(hsv_target.item(j,i,1)/255*(scale-1))]
        backP_img_u[j,i] = backP_img[j,i] * 255

gray_hist = np.zeros(256)
# 정규화된 히스토그램 생성
norm_hist = np.zeros(256,dtype=np.float)

# 기본 히스토그램을 구한다.
for i in range(backP_img_u.shape[1]):
    for j in range(backP_img_u.shape[0]):
        gray_hist[backP_img_u.item(j,i)]+=1
# 정규화 시켜서 저장한다.
for i in range(256):
    norm_hist[i] = gray_hist[i] / (backP_img_u.shape[0]*backP_img_u.shape[1])

vwlist = []
#vwlist2 = [] #without weight

for i in range(256): #T값을 결정하기위해서 1부터~255단계까지 바꾸어 나간다
    w0 = 0.0
    w1 = 0.0
    u0 = 0.0
    u1 = 0.0
    v0 = 0.0
    v1 = 0.0
    for j in range(i):
        w0 += norm_hist[j] #T가 1이라면  정규화된 값을 넣고
    for j in range(i+1,256):
        w1 += norm_hist[j] # 나머지값(2부터255까지 누적값 더하기)을 w1에넣고
        
    if w0 != 0:
        for j in range(i):
            u0 += j*norm_hist[j]
        u0 /= w0
        for j in range(i):
            v0 += norm_hist[j]*(j-u0)**2
        v0 /= w0

    if w1 != 0:
        for j in range(i+1,256):
            u1 += j*norm_hist[j]
        u1 /= w1
        for j in range(i+1,256):
            v1 += norm_hist[j]*(j-u1)**2
        v1 /= w1

    v_within = w0 * v0 + w1 * v1
    #v_within2 = v0 + v1 #without weight
    vwlist.append(v_within)
    #vwlist2.append(v_within2) #without weight
    #if v_within < best:
        #best = v_within
        #best_t = i
        #T_max[0] = i
        #T_max[1] = v_within

#print(T_max)
#print(best, best_t)

#print(vwlist)
t_argmin = np.argmin(vwlist)
print(t_argmin, vwlist[t_argmin])

binary = np.zeros((backP_img_u.shape[0],backP_img_u.shape[1]),dtype=np.uint8)

for i in range(backP_img_u.shape[0]):
    for j in range(backP_img_u.shape[1]):
        if backP_img_u[i,j] >= t_argmin:
            binary[i,j] = 255
        else:
            binary[i,j] = 0

# 이미지를 출력한다. imshow함수는 입력되는 배열의 값이 소수일 경우 [0.0, 1.0]의 범위를 [0, 255]에 매핑하여 변환해 출력해준다.
cv.imshow('img',backP_img)
cv.imshow('binary img',binary)
cv.waitKey(0)
cv.destroyAllWindows()