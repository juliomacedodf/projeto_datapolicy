Scraping de Eventos da ALESC
Este projeto realiza o scraping de eventos da página da Assembleia Legislativa de Santa Catarina (ALESC), coletando informações sobre os eventos, como nome, data, local, organizador, telefone e e-mail. Os dados são armazenados em um banco de dados MongoDB.

Tecnologias Utilizadas
Python
BeautifulSoup
Requests
Pandas
MongoDB
Docker
Docker Compose

Como Rodar o Projeto
Requisitos
Docker
Docker Compose




Execute o Docker Compose:
docker-compose up --build

Acesse o Mongo Express no navegador em:
http://localhost:8081

Estrutura de Diretórios
docker-compose.yml: Configuração do Docker Compose.
scraper.py: Script Python para o scraping e inserção dos dados no MongoDB.
requirements.txt: Dependências do projeto.


Licença
MIT License
