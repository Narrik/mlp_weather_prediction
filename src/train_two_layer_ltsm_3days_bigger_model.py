import os
import xarray as xr
import train_ltsm

means = xr.load_dataarray('data/baseline_mean.nc')
stds = xr.load_dataarray('data/baseline_std.nc')

DATADIR = os.getenv('DATASET_DIR', '/afs/inf.ed.ac.uk/user/s16/s1660124/datasets/')
OUT_DIR = os.getenv('SAVE_DIR', '/afs/inf.ed.ac.uk/user/s16/s1660124/output_baseline_ltsm/')

# Load the geo500 and temp850 data and merge
z = xr.open_mfdataset(
    f'{DATADIR}geopotential_500/*.nc',
    combine='by_coords',
    parallel=True,
    chunks={'time': 10}

)
t = xr.open_mfdataset(
    f'{DATADIR}temperature_850/*.nc',
    combine='by_coords',
    parallel=True,
    chunks={'time': 10}

)
ds = xr.merge([z, t], compat='override')

levels_per_variable = {'z': None, 't': None}

if __name__ == '__main__':
    train_ltsm.train(
        ds=ds,
        means=means,
        stds=stds,
        levels_per_variable=levels_per_variable,
        filters=[64, 64, 64, 64, 64, 64, 2],
        kernels=[5, 5, 5, 5, 5, 5, 5],
        lr=1e-4,
        activation='elu',
        dr=0,
        batch_size=64,
        patience=10,
        model_save_fn=OUT_DIR,
        pred_save_fn=os.path.join(OUT_DIR, 'predictions'),
        train_years=('1979', '2014'),
        valid_years=('2015', '2016'),
        test_years=('2017', '2018'),
        lead_time=3 * 24,
        seq_length=8,
        gpu=0,
        iterative=False,
        weights='/home/s1660124/output_ltsm_3days_large_model/models/weights.37-0.32.hdf5'
    )
