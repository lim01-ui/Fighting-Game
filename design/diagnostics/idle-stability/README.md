# Idle alignment fix

Oni, NULL and Sanya had unevenly positioned idle drawings within their atlas
columns. Column-centre origins caused visible sideways jumps on frame changes.

The corrected manifests use the actual boot soles. Their final rendered foot
baseline is aligned after pixel scaling, the extra player bob is disabled,
and idle frames play every 240ms. The original artwork is preserved.

- [Before](idle-before.gif)
- [After](idle-after.gif)

Regenerate the current preview with `python -B tools/preview_idle_stability.py`.
The regression check exercises the complete loop in both facing directions,
checks stable footprints and floor contact, and ensures the sprites still animate.
