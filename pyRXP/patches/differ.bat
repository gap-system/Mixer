@echo off
rem command used to get patch differences
diff -rc -I"Copyright (c) 1997" -I"$Header$Id:" -x"Entries" %1 %2 > %3
