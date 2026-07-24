# Bucket and prefix layout

Known validated SHboost24 public layout from local testing:

- Endpoint: `https://s3.data.aip.de:9000`
- Bucket: `shboost2024`
- Prefix: `shboost_08july2024_pub.parq/`
- Common parquet glob:

```text
s3://shboost2024/shboost_08july2024_pub.parq/*.parquet
```

Observed related public objects/releases in earlier exploration:
- `shboost_08july2024_pub.parq/`
- `shboost_09Oct2024_pub.parq/`
- `shboost_09Oct2024_render.parq/`

Operational guidance:
- treat exact release prefixes as data-release-specific;
- record which release a workflow used;
- cache reusable subsets locally as Parquet for reproducibility and speed.
