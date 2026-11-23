# Camera (PC Webcam)

**Module**: Camera

## Description

Takes pictures with a webcam or any other camera that Windows offers to OpenCV, and saves them as JPG or PNG files.
The driver returns the path of each picture, so the Camera module and image widgets can show it.

## Requirements

- Windows with a camera that is not in use by another program.
- No extra libraries: OpenCV, NumPy and Pillow ship with SweepMe!.

## Usage

1. Add the Camera module and select this driver.
2. Press *Find ports*: the port list holds the indices of the cameras that can be opened, starting at 0. With several
   cameras, try which index belongs to which camera. An empty port uses index 0.
3. Choose the **FileFormat** `jpg` or `png`.

Several cameras can be used at the same time with one Camera module each.

## Parameters

- **FileFormat**: `jpg` or `png`.

## Returns

- **image path**: path of the picture of the point, in the temporary folder of the run
  (`temp_Webcam<index>_<number>.<format>`).

## Notes

- At the start of the run a first picture `temp_Webcam<index>_before_start.<format>` is taken and discarded, as the
  first frames of many webcams are dark or not yet focused.
- The run stops with an error if the camera cannot be opened or delivers no image.

## Communication commands

- `take_picture(path)`: take a picture and save it at `path`; the extension decides the file format.
