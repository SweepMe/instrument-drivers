# Camera PC Webcam

This driver takes pictures with a webcam or another camera that OpenCV opens on the PC. For each measurement point, one
picture is saved into the temporary folder of the run, and its path is returned, so that the Camera module shows it.

---

### Requirements:

- The camera must be connected to the PC and installed in Windows.
- No further libraries are needed. OpenCV and numpy are part of SweepMe!.
- The Driver API needs pysweepme 1.6.1.5 or newer, shipped with SweepMe! 1.6.1.9.

---

### Usage:

- **Port** is the index of the camera: `0` for the first camera, `1` for the second, and so on. **Find Ports** lists
  the cameras that can be opened. Without a port, camera `0` is used.
- At the start of the run, the camera is opened and one picture is taken and dropped, because the first pictures of
  many webcams are too dark.
- For each measurement point, a picture is saved as `temp_Webcam<index>_<number>.<format>` into the temporary folder.
- At the end of the run, the camera is released for other programs.
- Several cameras: add one Camera module per camera, each with its own index.

---

### Parameters:

- **FileFormat**: `jpg` or `png`, the file format of the saved pictures.

---

### Measurement Output:

- **image path**: the path of the saved picture, without unit.

---

### Communication commands:

- `get_image()`: takes a picture and returns its pixels as an array of height x width x 3 color values (RGB) from
  0 to 255.
- `save_picture(path)`: takes a picture and saves it to `path`; the file format follows the extension (`.jpg`,
  `.jpeg` or `.png`).
- `get_picture_bytes(file_format)`: takes a picture and returns the bytes of a JPEG or PNG file, e.g. to show the
  camera live in a program. It is a plain function, not a communication command, because commands answer no bytes.
- `makePicture(pic_path)`: the name of earlier versions; it calls `save_picture`.

---

### Known limitations:

- Resolution, exposure and gain are not set: OpenCV's defaults apply (640 x 480 pixels with the webcam this driver
  was tested with).
- Cameras are known only by their index. Which camera has which index decides Windows; unplugging a camera can
  shift the indices of the others.
- **Find Ports** stops at the first index that cannot be opened, and at most 10 cameras are tried.
- A camera that is used by another program cannot be opened; the run stops with a message.
