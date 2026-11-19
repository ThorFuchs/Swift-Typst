# Repeated and concurrent compilation probe

After building the local artifact, run:

```sh
swift run --package-path Tests/Stress -c release Stress
```

This performs 400 sequential and 240 task-group calls using a short valid PDF
document and four malformed or missing-resource cases. It checks the PDF
signature for successful calls and structured diagnostics for failures. CI runs
it on macOS ARM64. It is a focused regression probe: it is not a memory leak
test, untrusted-input sandbox, benchmark, exhaustive fuzzer or proof of thread
safety on every platform.
