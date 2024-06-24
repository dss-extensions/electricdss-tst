# electricdss-tst

This repository includes a filtered copy of the [OpenDSS SVN repository](https://svn.code.sf.net/p/electricdss/code/trunk), including only the most relevant sample DSS scripts (examples and tests) for the [DSS C-API/AltDSS](https://github.com/dss-extensions/dss_capi/) and the downstream projects, like [DSS-Python](https://github.com/dss-extensions/DSS-Python/). There are also some extra samples.

The upstream copy is on branch `opendss-official-svn`, while the `master` branch will contain specific modifications.

Since June 2024, many duplicated files were removed relative `redirect`/`compile` commands (some inside single-line wrapper scripts) are used. Some files were near duplicated. After investigation, many of those were intended to be duplicated but diverged after small changes after several years. This means that if you compare some folders here with the ones from the upstream copy, you will notice small differences (besides file paths), and most of those are intended. When in doubt, both the repo history and `git blame` may expose what happened here.

Initially, we used symbolic links for the duplicate files, but the user experience is worse since the ZIP extraction tools don't work great on Windows.

---

This repository was created to more easily track upstream changes without all non-essential files, originally for testing `dss_capi` and `dss_python`. In comparison to the official SVN, this is lightweight, resulting in less than 40 MB in total, including the (almost full) history of the OpenDSS public files. The full history, including binary files and more, is almost 2.3 GB.

Since the official SVN repository is partially corrupted from revisions 2142 to 2161, we skip those here to avoid further issues.
If you need to clone the official SVN to reproduce the `opendss-official-svn` branch, you can use [`git-svn`](https://git-scm.com/docs/git-svn) like this:

```
git svn clone -r1:2141 --include-paths="^((License\.txt)|Test|((Version7\/)*(Version8\/)*(Parallel_Version\/)*Distrib\/(IEEETestCases\/|EPRITestCircuits\/|Examples\/|License\.txt))).*" --ignore-paths="(x64\.zip)|(x86.zip)|(.*\.(avi|pdf|ocx|ppt|doc|exe|user|suo|7z|zip|obj|AVI|PDF|OCX|PPT|DOC|EXE|USER|SUO|7Z|ZIP|OBJ))|(.*\/(Debug|Excel|bin|obj|Release|Direct_DLL))" https://svn.code.sf.net/p/electricdss/code/trunk electricdss-tst
cd electricdss-tst
git svn fetch -r2162:HEAD
```

This will skip those bad revisions. If you need the full history, you can just remove the long `--ignore-paths="..."` parameter. For fetching new SVN branches, you can use `git svn rebase`.

For an equivalent repository containing only the Pascal source-code, see the (archived, historical) [electricdss-src](https://github.com/dss-extensions/electricdss-src/). The code from `electricdss-src` is now hosted on the [`opendss-official-svn-v8` branch](https://github.com/dss-extensions/dss_capi/tree/opendss-official-svn-v8/) of the [DSS C-API library repository](https://github.com/dss-extensions/dss_capi/).
