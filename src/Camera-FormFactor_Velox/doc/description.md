# Camera FormFactor Velox

This driver controls the camera functions of FormFactor Velox wafer probers through the Velox Message Server. At
every measurement point, it saves an image of the selected camera and returns the path of the image file.

---

### Requirements:

- The Velox software must be installed and running on the prober PC. Velox has to be started before the measurement.
- No additional Python packages have to be installed. The `velox` package ships with the driver in its `libs` folder.

---

### Parameters:

- **Port**: Use `localhost` when SweepMe! runs on the same PC as Velox. For remote control via TCP/IP, enter the IP
  address of the Velox PC, either as a plain address `192.168.xxx.xxx` or with a specific socket as
  `IP:xxx.xxx.xxx.xxx; Port:xxxx`. The default socket is `1412`.
- **Camera**: The camera mount position whose image is saved, e.g. Scope, Platen or Chuck.
- **Mode**: *Raw image* saves the camera image only, *Screenshot* saves the image with the overlays visible in the
  camera view.
- **FileFormat**: bmp, jpg or png.
- **KeepLast**: If checked, no running number is appended to the file name, so each image overwrites the previous one
  and only the last image is kept.
- **Custom save name**: Prefix of the file name. If empty, `Velox_<Camera>` is used. A running number is appended
  unless **KeepLast** is checked.
- **Custom save folder**: Velox can only save the acquired images to a file, it cannot send them via TCP/IP. When
  using remote control, choose a folder on the Velox PC or on a common file share. If empty, the images are saved in
  the SweepMe! temp folder together with the other measurement data.

---

### Camera light:

The light of the selected camera is switched on right before each image is taken and switched off afterwards, also
if taking the image fails. Shutter, gain, brightness and the other light settings of the camera are not changed; set
them in Velox.
