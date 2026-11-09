/* Animation Dashboard.app starter. Runs Python inside the app's own process, so macOS shows
   "Animation Dashboard" and its icon in the Dock instead of "Python".
   VENV_SITE and APP_PY are filled in by build_app.sh. */
#include <Python.h>
#include <libgen.h>
#include <limits.h>
#include <mach-o/dyld.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    char exe[PATH_MAX], real[PATH_MAX], icon[PATH_MAX];
    uint32_t n = sizeof exe;
    if (_NSGetExecutablePath(exe, &n) != 0 || !realpath(exe, real)) return 1;
    snprintf(icon, sizeof icon, "%s/../Resources/PlanDashboard.icns", dirname(real));

    setenv("PYTHONPATH", VENV_SITE, 1);
    setenv("PYTHONNOUSERSITE", "1", 1);
    setenv("PYTHONDONTWRITEBYTECODE", "1", 1);

    char *args[] = {argv[0], APP_PY, "--icon", icon, NULL};
    return Py_BytesMain(4, args);
}
