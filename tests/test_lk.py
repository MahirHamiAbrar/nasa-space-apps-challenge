import lightkurve as lk

# Download light curve for a specific object
search_result = lk.search_lightcurve('TESS 119', mission='TESS')
lc = search_result.download()
lc.
lc.plot()
