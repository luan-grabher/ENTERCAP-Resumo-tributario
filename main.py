# atualiza pip e instala as dependencias
#import os

try:
    #os.system('python -m pip install --upgrade pip')
    #os.system('pip install -r requirements.txt')
    #os.system('cls')

    from src.menu.menu import main

    main()

except Exception as e:
    print('Erro inesperado durante a execução:\n\n' + str(e))
    exit(1)

exit(0)