# DigiTemp Exporter

DigiTemp Exporter is a simple Prometheus metrics exporter for DigiTemp
temperature sensors. It reads from a temperature sensor every 1 second, and the
most recent reading is made available as the metric `digitemp_temperature`.

For convenience, DigiTemp Exporter has been published as a public Docker image.
You can try it out as follows:

```
$ docker run --rm -p 8000:8000 --device /dev/ttyUSB0 \
  ghcr.io/anibali/digitemp-exporter \
  python digitemp_exporter.py --port=8000 --device=/dev/ttyUSB0
```

You can replace `/dev/ttyUSB0` with whatever device the temperature sensor is
connected to, and `8000` with whatever port you want the metric server to run
on.
