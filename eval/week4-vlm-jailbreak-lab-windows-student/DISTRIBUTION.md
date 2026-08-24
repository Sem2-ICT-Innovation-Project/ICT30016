# Student Distribution

The full instructor folder is large because `hf_cache` contains the local
Qwen2-VL model. Do not put `hf_cache` in the student download. Share a small lab
zip instead, then let each student download the model once on their own machine.

## Instructor packaging

From this folder:

```powershell
.\make_student_package.ps1
```

Upload the generated zip:

```text
dist\vlm-jailbreak-lab-windows-student.zip
```

The package excludes:

- `hf_cache`
- generated result folders such as `code\outputs_vlm_figstep_tiny`
- Python cache files

## Student setup

Students should extract the zip under the same parent folder as
`python-portable`, for example:

```text
ICT30016_Agent\
  python-portable\
  vlm-jailbreak-lab-windows-student\
```

Then run:

```bat
student_setup.bat
00_smoke_test.bat
05_demo_one.bat
```

`student_setup.bat` needs internet access. It installs Python dependencies and
downloads `Qwen/Qwen2-VL-2B-Instruct` into the local `hf_cache` folder. After
that, the normal demo scripts run from the local cache.

## Offline classroom option

If students cannot download several GB during class, prepare the model cache in
advance on a lab machine. The expected layout is:

```text
vlm-jailbreak-lab-windows-student\
  hf_cache\
    hub\
      models--Qwen--Qwen2-VL-2B-Instruct\
```

This cache is too large for the normal lab zip, so distribute it separately only
when your course and network policy allow it.

## Responsible-use note

Do not distribute generated `results_*.jsonl` files or model outputs. The lab
package should contain the teaching code and official evaluation assets only.
