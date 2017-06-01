# Project One: Search and Sample Return


### Myles Callan


## Section I

_Describe in your writeup (and identify where in your code) how you modified or added functions to add obstacle and rock sample identification_

**samples:** For the samples, I used `cv2`. Based on the examples used on this page: [Tracking colored objects in OpenCV](http://aishack.in/tutorials/tracking-colored-objects-opencv/ "Title"), it was relatively straightforward to find an upper and lower threshold for the gold color of the samples:

```
hsv_thresh_lower=(20, 100, 100)
hsv_thresh_upper=(30, 255, 255)
```


I developed this in the **Color Thresholding** section of the ***Rover Project Test Notebook*** and in the `process_image()`  function of the project. This approached worked well for both the still image and the test movie in the notebook and had no problem detecting samples in the project.

**Navigable Ground and Obstructions** I didn't use `cv2` for these regions as I couldn't find upper and lower bounds for the navigable environment. So, this rates as a TODO.

Instead, I used `numpy` with a lower threshold for navigable ground:

```
rgb_thresh=(170, 170, 170)
```

For Obstructions, I used the binary inverse of the Navigable Ground array, which worked well. 

## Section II

_Describe in your writeup how you modified the_ `process_image()` _to demonstrate your analysis and how you created a worldmap. Include your video output with your submission._

The steps in `process_image()` are:

- It is passed an image, from the perspective of the Rover.
- The current x,y positions and yaw are obtained from `data`.
- The current image is mapped onto the area using perspective transform
- The visual information - navigable ground, obstructions and samples - is extracted by applying color thresholds.
- The masked images are mapped onto the world map by aligning the coordinaate (using polor coordinates).
- The output is an image with the masks applied to different layers.

See the file `mcallan_NB_test.mp4` for the video output from my notebook.

## Section III

`perception_step()` _and_ `decision_step()` _functions have been filled in and their functionality explained in the writeup._

### `perception_step()`

The `perception_step()` function was modified in the same way as `process_map()` was. The only addition was an attempt to increase the fidelity of the world mapping by stopping mapping when pitch and roll were too high. The condition used were:

```
    if (Rover.pitch < 0.5) and (Rover.roll < 350):
```
which was derived from trial and error.

And I used `3` as the value for the bottom offset for the Rover, in addition to my source, for the dimensions of the pictures being taken by the Rover's camera:

```
    source = np.float32([[ 13, 140], [302 ,140 ], [202,96 ], [119 ,96 ] ])
```    

As you will see from the video supplied, while there was no problem with the `Rover.worldmap`, the `Rover.vision_image` did not update (and so doesn't show in the video). As this determines the `near_sample` value, it did not change even if the Rover drove over a sample. So, I wasn't able to pick up any samples.

I spent way too much time trying to find out what was causing this and couldn't find the problem. If you could make a suggestion about this, I'd be only too happy to resolve this and re-submit this project.


### `decision_step()`

I spent too much time trying to get `Rover.vision_image` updating data and too little time on the decision step.

I did make some changes to try to move the Rover when it was stuck, which were partly successful.

I also used the standard deviation of the view angles to clip the steering angle, which in hindsight was an odd choice:

```
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -1*np.std(Rover.nav_angles * 180/np.pi), 1*np.std(Rover.nav_angles * 180/np.pi))
```



## Section IV

_By running_ `drive_rover.py` _and launching the simulator in autonomous mode, your rover does a reasonably good job at mapping the environment._

_The rover must map at least 40% of the environment with 60% fidelity (accuracy) against the ground truth. You must also find (map) the location of at least one rock sample_

See the video included in the submission: `mcallan_autonomous.mp4`



