from abc import ABC, abstractmethod
from datetime import datetime
from time import sleep
import textwrap


class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """ Classe que armazena os dados de uma pessoa física."""
    def __init__(self, cpf: str, nome: str, data_nascimento: str, endereco: str):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


class Historico:
    """ Registra o histórico de transações do cliente."""
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
        })


class Conta: 
    """ Classe que armazena os dados referentes a conta do cliente."""
    def __init__(self, numero: int, cliente: Cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor) -> bool:
        if valor <= 0:
            print('\nOperação falhou! O valor informado é inválido.')
            return False
        if valor > self._saldo:
            print('\nOperação falhou. Você não tem saldo suficiente.')
            return False
        self._saldo -= valor
        print('\nSaque efetuado com sucesso!')
        sleep(2)
        return True

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('Transação efetuada com sucesso!')
            sleep(2)
            return True
        else:
            print('A operação falhou! Digite um valor válido!')
            return False


class ContaCorrente(Conta):
    """ Função que executa as operações possíveis na conta corrente"""
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([
            transacao for transacao in self.historico.transacoes
            if transacao['tipo'] == "Saque"
        ])

        if valor > self.limite:
            print('Operação falhou! Valor informado é maior que o limite.')
            sleep(2)
            return False

        if numero_saques >= self.limite_saques:
            print('Operação falhou! Número máximo de saques alcançado.')
            sleep(2)
            return False

        return super().sacar(valor)

    def __str__(self):
        return f'Agência: {self.agencia} \nC/C: {self.numero} \nTitular: {self.cliente.nome}'


class Transacao(ABC):
    """Classe abstrata."""
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    """Imprime o menu de opções na tela."""
    opcoes = """
    === Menu ===
    [1] - Depositar
    [2] - Sacar
    [3] - Extrato
    [4] - Nova Conta
    [5] - Listar contas
    [6] - Novo usuário
    [7] - Sair
    ========================
    => """
    return input(textwrap.dedent(opcoes))


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('Cliente não possui conta.')
        return None
    
    return cliente.contas[0]  


def filtrar_usuario(cpf, usuarios):

    usuarios_filtrados = [cliente for cliente in usuarios if cliente.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def depositar(usuarios):
    """ Função que retira valor de uma conta, definido pelo usuário."""
    cpf = input('Informe o CPF: ')
    cliente = filtrar_usuario(cpf, usuarios)

    if not cliente:
        print('Cliente não encontrado.')
        sleep(2)
        return

    valor = float(input('Informe o valor do depósito: '))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)


def sacar(usuarios):
    """Cria uma função que saca de uma conta um valor."""
    cpf = input('Informe o CPF: ')
    cliente = filtrar_usuario(cpf, usuarios)

    if not cliente:
        print('Cliente não encontrado.')
        sleep(2)
        return

    valor = float(input('Informe o valor do saque: '))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)


def ver_extrato(usuarios):
    """ Mostra o saldo da conta."""
    cpf = input('Informe o CPF: ')
    cliente = filtrar_usuario(cpf, usuarios)

    if not cliente:
        print('Cliente não encontrado.')
        sleep(2)
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print('=' * 20, 'EXTRATO', '=' * 20)
    transacoes = conta.historico.transacoes

    if not transacoes:
        print('Não há transações registradas.')
    else:
        for transacao in transacoes:
            print(f"{transacao['tipo']}: R$ {transacao['valor']:.2f} em {transacao['data']}")

    print(f'\nSaldo atual: R$ {conta.saldo:.2f}')
    print('=' * 50)


def criar_usuario(usuarios):
    """Cria um novo cliente com os seguintes dados: 
    usuário:
    - Nome, data de nascimento, cpf e endereço.
    - Endereço: é uma string formado por:
        logradouro, número -bairro -
        cidade/ sigla estado. Deve ser armazenado somentos os números de CPF. Não 
        podemos cadastrar dois usuários no mesmo CPF.
    """
    cpf = input('Informe o CPF (somente números): ')
    cliente = filtrar_usuario(cpf, usuarios)

    if cliente:
        print('Já existe cliente com esse CPF!')
        sleep(2)
        return

    nome = input('Informe o nome completo: ')
    data_nascimento = input('Informe a data de nascimento (dd/mm/aaaa): ')
    endereco = input('Informe o endereço (logradouro, número, bairro, cidade/sigla estado): ')

    novo_cliente = PessoaFisica(cpf, nome, data_nascimento, endereco)
    usuarios.append(novo_cliente)

    print('Cliente criado com sucesso!')
    sleep(2)


def criar_conta_corrente(numero_conta, usuarios, contas):
    """ armazena em uma lista, composta por: agência, número da conta e usuário.
    O número da conta é sequêncial, iniciando em 1. O número da agência é fixo 
    '0001'. O usuário pode ter mais de uma conta, mas uma conta pertence somente
    a um usuário."""
    cpf = input('Informe o CPF do usuário (somente números): ')
    cliente = filtrar_usuario(cpf, usuarios)

    if not cliente:
        print('Cliente não encontrado.')
        sleep(2)
        return

    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print('Conta criada com sucesso!')
    sleep(2)


def listar_contas(contas):
    """Lista todas as contas já criadas."""
    for conta in contas:
        print('=' * 40)
        print(conta)
        sleep(3)


def main():
    """Função principal, que vai executar todo o sistema."""
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == '1':
            depositar(usuarios)
        elif opcao == '2':
            sacar(usuarios)
        elif opcao == '3':
            ver_extrato(usuarios)
        elif opcao == '4':
            numero_conta = len(contas) + 1
            criar_conta_corrente(numero_conta, usuarios, contas)
        elif opcao == '5':
            listar_contas(contas)
        elif opcao == '6':
            criar_usuario(usuarios)
        elif opcao == '7':
            print('\nObrigado por usar nosso sistema bancário!')
            break
        else:
            print('\nOpção inválida!')
            sleep(2)


if __name__ == '__main__':
    main()
