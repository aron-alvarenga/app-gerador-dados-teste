import sys
import os
import csv
import json
import random
from typing import Dict, List, Any

import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QLineEdit, QTableWidget, 
    QTableWidgetItem, QFileDialog, QCheckBox, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt
from faker import Faker

class DatabaseConnectionDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Conexão com Banco de Dados')
        
        layout = QFormLayout()
        
        self.hostInput = QLineEdit()
        self.hostInput.setText('localhost')
        layout.addRow('Host:', self.hostInput)
        
        self.userInput = QLineEdit()
        layout.addRow('Usuário:', self.userInput)
        
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
        layout.addRow('Senha:', self.passwordInput)
        
        self.databaseInput = QLineEdit()
        layout.addRow('Banco de Dados:', self.databaseInput)
        
        self.conectarBtn = QPushButton('Conectar')
        self.conectarBtn.clicked.connect(self.testarConexao)
        layout.addRow(self.conectarBtn)
        
        self.statusLabel = QLabel('')
        layout.addRow(self.statusLabel)
        
        self.setLayout(layout)
    
    def testarConexao(self):
        try:
            conexao = mysql.connector.connect(
                host=self.hostInput.text(),
                user=self.userInput.text(),
                password=self.passwordInput.text(),
                database=self.databaseInput.text()
            )
            conexao.close()
            self.statusLabel.setText('Conexão bem-sucedida!')
            self.statusLabel.setStyleSheet('color: green')
        except mysql.connector.Error as erro:
            self.statusLabel.setText(f'Erro de conexão: {erro}')
            self.statusLabel.setStyleSheet('color: red')

class TestDataGenerator:
    def __init__(self, connection_params: Dict[str, str]):
        """
        Inicializa a conexão com o banco de dados e utilitários de geração de dados.
        
        Args:
            connection_params (dict): Parâmetros de conexão MySQL
        """
        self.connection = mysql.connector.connect(**connection_params)
        self.cursor = self.connection.cursor(dictionary=True)
        self.faker = Faker('pt_BR')
        
    def listar_tabelas(self):
        """
        Lista todas as tabelas do banco de dados.
        
        Returns:
            list: Lista de nomes das tabelas
        """
        self.cursor.execute("SHOW TABLES")
        return [table[f"Tables_in_{self.connection.database}"] for table in self.cursor.fetchall()]
    
    def analisar_estrutura_tabela(self, tabela: str):
        """
        Analisa a estrutura de uma tabela específica.
        
        Args:
            tabela (str): Nome da tabela
        
        Returns:
            list: Detalhes das colunas da tabela
        """
        self.cursor.execute(f"DESCRIBE {tabela}")
        return self.cursor.fetchall()
    
    def gerar_dados_teste(self, tabela: str, quantidade: int):
        """
        Gera dados de teste para uma tabela.
        
        Args:
            tabela (str): Nome da tabela
            quantidade (int): Número de registros a serem gerados
        
        Returns:
            list: Dados de teste gerados
        """
        colunas = self.analisar_estrutura_tabela(tabela)
        dados_gerados = []
        
        for _ in range(quantidade):
            registro = {}
            for coluna in colunas:
                nome = coluna['Field']
                tipo = coluna['Type'].lower()
                
                if 'nome' in nome.lower() or 'name' in nome.lower():
                    registro[nome] = self.faker.name()
                elif 'email' in nome.lower():
                    registro[nome] = self.faker.email()
                elif 'cpf' in nome.lower():
                    registro[nome] = self.faker.cpf()
                elif 'telefone' in nome.lower() or 'phone' in nome.lower():
                    registro[nome] = self.faker.phone_number()
                elif 'data' in nome.lower() or 'date' in nome.lower():
                    registro[nome] = self.faker.date_between(start_date='-30y', end_date='today')
                elif 'int' in tipo:
                    registro[nome] = random.randint(1, 1000)
                elif 'decimal' in tipo or 'float' in tipo:
                    registro[nome] = round(random.uniform(0, 10000), 2)
                else:
                    registro[nome] = self.faker.text(max_nb_chars=50)
            
            dados_gerados.append(registro)
        
        return dados_gerados
    
    def exportar_dados(self, tabela: str, dados: List[Dict], formato: str, caminho_arquivo: str):
        """
        Exporta dados gerados em diferentes formatos.
        
        Args:
            tabela (str): Nome da tabela
            dados (list): Dados gerados
            formato (str): Formato de exportação (SQL, CSV, JSON)
            caminho_arquivo (str): Caminho do arquivo de saída
        """
        if formato == 'SQL':
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                for registro in dados:
                    colunas = ', '.join(registro.keys())
                    valores = ', '.join([f"'{str(val)}'" for val in registro.values()])
                    sql = f"INSERT INTO {tabela} ({colunas}) VALUES ({valores});\n"
                    f.write(sql)
        
        elif formato == 'CSV':
            df = pd.DataFrame(dados)
            df.to_csv(caminho_arquivo, index=False, encoding='utf-8')
        
        elif formato == 'JSON':
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)

class TestDataGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gerador de Dados de Teste')
        self.resize(800, 600)
        
        widget_central = QWidget()
        layout_principal = QVBoxLayout()
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)
        
        btn_conexao = QPushButton('Configurar Conexão')
        btn_conexao.clicked.connect(self.abrir_conexao)
        layout_principal.addWidget(btn_conexao)
        
        self.combo_tabelas = QComboBox()
        self.combo_tabelas.setEnabled(False)
        layout_principal.addWidget(QLabel('Selecione a Tabela:'))
        layout_principal.addWidget(self.combo_tabelas)
        
        layout_quantidade = QHBoxLayout()
        layout_quantidade.addWidget(QLabel('Quantidade de Registros:'))
        self.input_quantidade = QLineEdit()
        self.input_quantidade.setText('10')
        layout_quantidade.addWidget(self.input_quantidade)
        layout_principal.addLayout(layout_quantidade)
        
        grupo_exportacao = QHBoxLayout()
        self.check_sql = QCheckBox('SQL')
        self.check_csv = QCheckBox('CSV')
        self.check_json = QCheckBox('JSON')
        grupo_exportacao.addWidget(self.check_sql)
        grupo_exportacao.addWidget(self.check_csv)
        grupo_exportacao.addWidget(self.check_json)
        layout_principal.addLayout(grupo_exportacao)
        
        btn_gerar = QPushButton('Gerar Dados')
        btn_gerar.clicked.connect(self.gerar_e_exportar)
        layout_principal.addWidget(btn_gerar)
        
        self.label_status = QLabel('')
        layout_principal.addWidget(self.label_status)
        
        self.gerador = None
    
    def abrir_conexao(self):
        self.dialog_conexao = DatabaseConnectionDialog()
        self.dialog_conexao.show()
        self.dialog_conexao.conectarBtn.clicked.connect(self.carregar_tabelas)
    
    def carregar_tabelas(self):
        try:
            conexao_params = {
                'host': self.dialog_conexao.hostInput.text(),
                'user': self.dialog_conexao.userInput.text(),
                'password': self.dialog_conexao.passwordInput.text(),
                'database': self.dialog_conexao.databaseInput.text()
            }
            
            self.gerador = TestDataGenerator(conexao_params)
            tabelas = self.gerador.listar_tabelas()
            
            self.combo_tabelas.clear()
            self.combo_tabelas.addItems(tabelas)
            self.combo_tabelas.setEnabled(True)
            
            self.dialog_conexao.close()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha na conexão: {str(e)}')
    
    def gerar_e_exportar(self):
        if not self.gerador:
            QMessageBox.warning(self, 'Aviso', 'Configure a conexão primeiro')
            return
        
        tabela = self.combo_tabelas.currentText()
        quantidade = int(self.input_quantidade.text())
        
        try:
            dados = self.gerador.gerar_dados_teste(tabela, quantidade)
            
            formatos = []
            if self.check_sql.isChecked():
                formatos.append('SQL')
            if self.check_csv.isChecked():
                formatos.append('CSV')
            if self.check_json.isChecked():
                formatos.append('JSON')
            
            if not formatos:
                QMessageBox.warning(self, 'Aviso', 'Selecione pelo menos um formato de exportação')
                return
            
            for formato in formatos:
                caminho, _ = QFileDialog.getSaveFileName(
                    self, 
                    f'Salvar arquivo {formato}', 
                    f'{tabela}_dados_teste.{formato.lower()}',
                    f'Arquivos {formato} (*.{formato.lower()})'
                )
                
                if caminho:
                    self.gerador.exportar_dados(tabela, dados, formato, caminho)
            
            self.label_status.setText(f'Dados gerados para {tabela}')
            self.label_status.setStyleSheet('color: green')
        
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha na geração de dados: {str(e)}')

def main():
    app = QApplication(sys.argv)
    
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    gerador_gui = TestDataGeneratorGUI()
    gerador_gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()