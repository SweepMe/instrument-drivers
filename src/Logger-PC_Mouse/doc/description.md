# Logger (PC Mouse)

**Module**: Logger

## Description

Reads the position of the mouse cursor and the state of the left and right mouse button, e.g. to record a path drawn
with the mouse or to let the user mark points on the screen.

## Requirements

- Windows. No instrument and no extra libraries.

## Usage

Add the Logger module and select this driver. It has no parameters.

## Returns

- **x**, **y** (px): cursor position on the primary screen. The origin (0, 0) is the **lower** left corner, y points
  upwards, so a plot of y over x looks like the path on the screen. Positions on other monitors lie outside the
  primary screen. Both are NaN while Windows shows no cursor, e.g. while an elevated Task Manager has the focus.
- **x_press**, **y_press** (px): the position while the left button is pressed, else NaN.
- **Left_clicked**, **Right_clicked**: the Windows key state of the button: negative while the button is pressed;
  the lowest bit toggles with every click.

The coordinates are the same as those of the Switch driver *PC Mouse*, so a recorded position can be swept there.

## Communication commands

- `get_position()`: cursor position (x, y) in px, origin lower left.
- `get_screen_size()`: width and height of the primary screen in px.
- `get_button_states()`: Windows key state of the left and right button.
