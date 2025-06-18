Command:

```sh
gcloud alpha monitoring policies create --project <project-id> --policy-from-file <file dir>
```

Example

```sh
gcloud alpha monitoring policies create --project prj-monitoring-infra --policy-from-file "Compute Engine/VM Instance - High CPU Utilization.json"
```