# electricdss-tst
This includes a filtered copy of the [OpenDSS SVN repository](https://svn.code.sf.net/p/electricdss/code/trunk), including only the most relevant sample DSS scripts (examples and tests) for the [dss_capi](https://github.com/PMeira/dss_capi/) and [dss_python](https://github.com/PMeira/dss_python/) projects.

The upstream copy is on branch `opendss-official-svn`, while the `master` branch will contain specific modifications.

This repository was created to more easily track upstream changes without all non-essential files for testing `dss_capi` and `dss_python`, resulting in less than 40 MB in total, including the (almost full) history of the OpenDSS public files. The full history, including binary files and more, is almost 2.3 GB.

Since the official SVN repository is partially corrupted from revisions 2142 to 2161, we skip those here to avoid further issues.
If you need to clone the official SVN to reproduce the `opendss-official-svn` branch, you can use [`git-svn`](https://git-scm.com/docs/git-svn) like this:

```
git svn clone -r1:2141 --include-paths="^((License\.txt)|Test|((Parallel_Version\/)*Distrib\/(IEEETestCases\/|EPRITestCircuits\/|Examples\/|License\.txt))).*" --ignore-paths="(x64\.zip)|(x86.zip)|(.*\.(avi|pdf|ocx|ppt|doc|exe|user|suo|7z|zip|obj|AVI|PDF|OCX|PPT|DOC|EXE|USER|SUO|7Z|ZIP|OBJ))|(.*\/(Debug|Excel|bin|obj|Release|Direct_DLL))" https://svn.code.sf.net/p/electricdss/code/trunk electricdss-tst
cd electricdss-tst
git svn fetch -r2162:HEAD
```

This will skip those bad revisions. If you need the full history, you can just remove the long `--ignore-paths="..."` parameter. For fetching new SVN branches, you can use `git svn rebase`.

For an equivalent repository containing only the Pascal source-code, see [electricdss-src](https://github.com/PMeira/electricdss-src/).
