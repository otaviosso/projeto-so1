# Simulador de rede de entregas
## Autores: Antony Muller Pereira e Otávio Scarparo Souza
## Uso
`python3 main.py [S] [C] [P] [A]`
## Detalhes da implementação
Há três funções principais, uma para encomendas, uma para veículos e outra para pontos.
### Encomendas
São gerados aleatoriamente um ponto de início e um de destino. Enquanto ela não for entregue a thread dorme.
### Veículos
É gerado aleatoriamente um ponto de início. Enquanto houverem encomendas não entregues ele recolhe as que estiverem em um determinado ponto e as entrega. Recolher encomendas é uma seção crítica, então é usada uma lock para prevenir que tenha mais de um veículo recolhendo no mesmo ponto.
### Pontos
A função avisa quando todas as encomendas forem retiradas.
