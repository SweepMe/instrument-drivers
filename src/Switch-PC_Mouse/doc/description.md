# Switch (PC Mouse)

**Module**: Switch

## Description

Moves the mouse cursor to the sweep value and can click there, e.g. to operate another program that has no remote
interface.

## Requirements

- Windows. No instrument and no extra libraries.

## Usage

1. Add the Switch module and select this driver.
2. Choose the **SweepMode**:
   - `Coordinates in px`: the sweep value is the position as `(x;y)`, `x;y` or `x,y` (use the SweepBox, as a comma
     separates values in the SweepEditor).
   - `Position x in px` or `Position y in px`: only one coordinate changes, the other one stays.
3. Check **Leftclick** to click the left button after each move.

The coordinates are pixels of the primary screen with the origin (0, 0) in the **lower** left corner and y pointing
upwards, the same as those of the Logger driver *PC Mouse*. Positions on other monitors lie outside the primary
screen.

Sequences saved with the earlier labels `Coordinates [(pix;pix)]`, `Position x [pix]` and `Position y [pix]` keep
working.

## Parameters

- **Leftclick**: click the left button after the cursor moved.

## Returns

Nothing.

## Communication commands

- `get_position()`, `set_position(x_position, y_position)`: cursor position in px, origin lower left.
- `get_screen_size()`: width and height of the primary screen in px.
- `left_click()`, `right_click()`, `double_click()`: click at the current position.
