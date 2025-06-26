from app import create_app

app = create_app()

if __name__ == "__main__":
    # print(app.config)
    app.run(debug=app.config['DEBUG'])
    

# debug=false (mode de produção)
#   -> não recarrega o servidor automaticamente
#   -> erros genericos sem o traceback
#   -> não expoe detalhes internos