## Create Alert Policy:

```sh
gcloud alpha monitoring policies create --project <project-id> --policy-from-file <file dir>
```

Example

```sh
gcloud alpha monitoring policies create --project prj-monitoring-infra --policy-from-file "Compute Engine/VM Instance - High CPU Utilization.json"
```

## List alerts policy

```sh
gcloud alpha monitoring policies list --project <project-id>"
```