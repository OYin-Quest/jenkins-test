
SET TARGET_SHARE=\\zhuradnasw02.prod.quest.corp\Store
SET TARGET_CREDS=prod\svc-ausbuilds Quest123
SET TARGET_ROOT=Z:\Datahub Builds\NightlyBuild\Skytap

IF NOT EXIST Z: (
  NET USE Z: /DEL & NET USE Z: %TARGET_SHARE% /USER:%TARGET_CREDS%
) ELSE (
  NET USE Z: | FINDSTR "Disconnected" && (
    NET USE Z: /DELETE
    NET USE Z: %TARGET_SHARE% /USER:%TARGET_CREDS%
  )
)

NET USE

python DropSkytapBuild.py "%TARGET_ROOT%"

python DropArtifactoryBuild.py