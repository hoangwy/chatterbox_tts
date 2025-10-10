#!/bin/bash
python3 -m build --sdist .
twine upload dist/chatterbox_tts-$(cat .latest-version.generated.txt).tar.gz
