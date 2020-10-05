#!/bin/sh
cat > src/buildtime.py <<EOF
date = "$(date)"
EOF

rm -f package.zip
cd src/
zip -0 ../package.zip *
cd ../
echo "#!/usr/bin/env python3" | cat - package.zip > package
chmod +x package
rm -f package.zip
