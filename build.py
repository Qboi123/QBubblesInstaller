from QCompiler.qcompiler import QCompilerPYZ, QCompilerPYC


pre_compiler = QCompilerPYC([], "QBubblesInstaller")
compiler = QCompilerPYZ("QBubblesInstaller", "QBubblesInstaller.pyz", "__init__:main", False, pre_compiler, True)
compiler.compile()
