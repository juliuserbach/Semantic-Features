import numpy as np
import cv2
from tools import utils
import pykitti
import matplotlib.pyplot as plt


def reprojection_error(depth_1, depth_2):
    indices = np.logical_and(depth_1 > 0, depth_2 > 0)
    errors = np.abs(depth_1[indices] - depth_2[indices])
    errors.sort()
    image = np.abs(depth_1 - depth_2)
    image[np.logical_not(indices)] = 0
    print("Number of errors < 0.5 m: {}".format(np.array(np.where(errors < 0.5)).shape[1]))
    plt.hist(errors, bins=1000)
    plt.show("Histogram of errors")
    mse = np.mean(np.square(errors[:5000]))
    print("Mean square error is: {}".format(mse))
    print("Root mean square error is: {}".format(np.sqrt(mse)))

    return image


if __name__ == '__main__':
    basedir = 'content/kitti_dataset/dataset'

    # Specify the dataset to load
    sequence = '04'

    # Load the data. Optionally, specify the frame range to load.
    # dataset = pykitti.odometry(basedir, sequence)
    dataset = pykitti.odometry(basedir, sequence)

    # Grab some data
    second_pose = dataset.poses[219]
    first_rgb = dataset.get_rgb(219)
    first_cam2 = dataset.get_cam2(219)
    velo = dataset.get_velo(219)
    baseline = dataset.calib.b_gray

    path = "/home/felix/vision_ws/Semantic-Features/content/kitti_dataset/dataset/sequences/04/disparity_2_new/219.png"
    disparity = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    P_cam2 = dataset.calib.P_rect_00
    T_cam2_velo = dataset.calib.T_cam0_velo

    fx = P_cam2[0, 0]

    rgb_img = np.asarray(first_cam2)
    P_cam2 = np.vstack([P_cam2, [0., 0., 0., 1.]])

    depth_img = utils.pcl_to_image(velo[:, :3], T_cam2_velo, P_cam2, (rgb_img.shape[0], rgb_img.shape[1]))

    depth_from_disp = utils.disparity_to_depth(disparity, fx, baseline, min_disparity=0)
    # depth_from_disp = cv2.GaussianBlur(depth_from_disp, (3, 3), 0)
    errors = reprojection_error(depth_img, depth_from_disp)

    f, ax = plt.subplots(2, 2, figsize=(15, 5))

    ax[0, 0].imshow(first_cam2)
    ax[0, 0].set_title('Left RGB Image (cam2)')

    ax[0, 1].imshow(depth_img)
    ax[0, 1].set_title('Depth from LIDAR')

    # depth_from_disp[np.where(depth_img > 0)] = depth_img[np.where(depth_img > 0)]
    ax[1, 1].imshow(depth_from_disp)
    ax[1, 1].set_title('Depth from disparity')

    ax[1, 0].imshow(errors)
    ax[1, 0].set_title('Reprojection error of disparity image.')

    plt.show()