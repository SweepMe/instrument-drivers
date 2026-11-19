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

- **Port** starts with the index of the camera: `0` for the first camera, `1` for the second, and so on. On Windows,
  **Find Ports** lists the cameras with what they are, e.g. `0: Integrated Camera, USB 04F2:B6EA rev 6218, serial
  0001`, without opening them; elsewhere it lists the indices of the cameras that can be opened. Only the index is
  used to open the camera, so a port of earlier versions (`0`) still works. Without a port, camera `0` is used.
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

- `get_identification()`: returns the camera's name, USB vendor and product id, revision and serial number as
  Windows lists them, e.g. `Integrated Camera, USB 04F2:B6EA rev 6218, serial 0001`. It takes no picture. The serial
  number is the one the camera reports over USB: many webcams report none (then it says `no serial number`), and
  integrated cameras often report a placeholder such as `0001`, which other cameras of the model share. Windows only.
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
  shift the indices of the others. On Windows, the driver opens the cameras through Media Foundation, whose order
  `get_identification` reads.
- On Windows, **Find Ports** also lists a camera that another program uses; it cannot be opened then. Elsewhere,
  **Find Ports** stops at the first index that cannot be opened, and at most 10 cameras are tried.
- A camera that is used by another program cannot be opened; the run stops with a message.
