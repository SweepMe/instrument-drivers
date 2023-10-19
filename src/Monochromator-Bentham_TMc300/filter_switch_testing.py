# %%
def set_fwheel_switch_wlns(filter_string):
    """Parse user inputs and write wln at which each filter is switched
    to memory (.atr file loaded in mem)
    """
    # FW pos 6 normally corresponds to shutter.
    # All FW values need to be overwritten otherwise from loaded
    # .atr file will be used
    # 0 typically signifies do not use/or used by default
    # ! first 0 is used not last --> need a tiny value for last 0

    """ parse the GUI entry """
    # if was a single value
    try:
        fixed_filt_pos = int(filter_string)
        # set_fhweel_pos(fixed_filt_pos)
        filter_list = [1, 2, 3, 4, 5]
        fwheel_wlns = (
            [0] * (fixed_filt_pos - 1) + [0.1] + [1000000] * (5 - fixed_filt_pos)
        )
        return
    except ValueError:
        # in case it was a settings string
        filter_readout = (
            filter_string.replace("<", "")
            .replace(">", "")
            .replace("nm", "")
            .replace(" ", "")
            .split("-")
        )
        # list filter indices
        filter_list = list(map(int, filter_readout[::2]))
        fwheel_wlns = [0] + list(
            map(float, filter_readout[1::2])
        )  # list filter wavelengths

        # FORMAT LIST --> complete and last 0 is small value
        for i in range(1, 7):
            if i not in filter_list:
                filter_list.insert(i - 1, i)
                fwheel_wlns.insert(i - 1, 0)
        # now make sure last consecutive 0 is a small value
        # find last consequitive 0
        print(filter_list, fwheel_wlns)
        bool_conseq = [
            (fwheel_wlns[i] == fwheel_wlns[i + 1]) & (fwheel_wlns[i] == 0)
            for i in range(len(fwheel_wlns) - 1)
        ]
        if any(bool_conseq):
            last_0_idx = len(bool_conseq) - bool_conseq[::-1].index(True)
            print("last idx", last_0_idx)
            fwheel_wlns[last_0_idx] = 0.1

    for f_pos, wln in zip(filter_list, fwheel_wlns):
        print(f_pos, wln)

    print("")


s_full = "1 <- 400 nm -> 2 <- 700 nm -> 3 <- 750 nm -> 4 <- 800 nm -> 5"
s_2 = "2"
s_partial1 = "1 <- 400 nm -> 2 <- 700 nm -> 4 <- 800 nm -> 5"
s_partial2 = " 2 <- 700 nm -> 3 <- 750 nm -> 4 <- 800 nm -> 5"

# set_fwheel_switch_wlns(s_full)
# print("2")
# set_fwheel_switch_wlns(s_2)
print("3")
set_fwheel_switch_wlns("3")
print("done")
set_fwheel_switch_wlns(s_partial1)
set_fwheel_switch_wlns(s_partial2)

# %%
