import sys
import os
import csv
import json
import random
from typing import Dict, List, Any
import datetime

import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QLineEdit, QTableWidget, 
    QTableWidgetItem, QFileDialog, QCheckBox, QMessageBox, QFormLayout,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from faker import Faker

class TailwindStyle:
    @staticmethod
    def apply_style(app):
        app.setStyle('Fusion')
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#ffffff'))
        palette.setColor(QPalette.WindowText, QColor('#1f2937'))
        palette.setColor(QPalette.Base, QColor('#f3f4f6'))
        palette.setColor(QPalette.AlternateBase, QColor('#e5e7eb'))
        palette.setColor(QPalette.ToolTipBase, QColor('#1f2937'))
        palette.setColor(QPalette.ToolTipText, QColor('#ffffff'))
        palette.setColor(QPalette.Text, QColor('#1f2937'))
        palette.setColor(QPalette.Button, QColor('#f3f4f6'))
        palette.setColor(QPalette.ButtonText, QColor('#1f2937'))
        palette.setColor(QPalette.BrightText, QColor('#ffffff'))
        palette.setColor(QPalette.Link, QColor('#3b82f6'))
        palette.setColor(QPalette.Highlight, QColor('#3b82f6'))
        palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
        app.setPalette(palette)

    @staticmethod
    def get_button_style():
        return """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """

    @staticmethod
    def get_input_style():
        return """
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                color: #1f2937;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                color: #1f2937;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 1px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgMTIgOCIgZmlsbD0ibm9uZSI+PHBhdGggZD0iTTEgMUw2IDZMMTEgMSIgc3Ryb2tlPSIjNkI4MkY2IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjwvc3ZnPg==);
                width: 12px;
                height: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                selection-background-color: #3b82f6;
                selection-color: white;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f3f4f6;
            }
        """

    @staticmethod
    def get_checkbox_style():
        return """
            QCheckBox {
                color: #1f2937;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #d1d5db;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border: 1px solid #3b82f6;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #3b82f6;
            }
        """

    @staticmethod
    def get_label_style():
        return """
            QLabel {
                color: #1f2937;
                font-weight: 500;
            }
        """

class DatabaseConnectionDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Conexão com Banco de Dados')
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        titulo = QLabel('Configuração de Conexão')
        titulo.setStyleSheet('font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 16px;')
        layout.addRow(titulo)
        
        self.hostInput = QLineEdit()
        self.hostInput.setText('localhost')
        self.hostInput.setStyleSheet(TailwindStyle.get_input_style())
        layout.addRow('Host:', self.hostInput)
        
        self.userInput = QLineEdit()
        self.userInput.setStyleSheet(TailwindStyle.get_input_style())
        layout.addRow('Usuário:', self.userInput)
        
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.passwordInput.setStyleSheet(TailwindStyle.get_input_style())
        layout.addRow('Senha:', self.passwordInput)
        
        self.databaseInput = QLineEdit()
        self.databaseInput.setStyleSheet(TailwindStyle.get_input_style())
        layout.addRow('Banco de Dados:', self.databaseInput)
        
        self.conectarBtn = QPushButton('Conectar')
        self.conectarBtn.setStyleSheet(TailwindStyle.get_button_style())
        self.conectarBtn.clicked.connect(self.testarConexao)
        layout.addRow(self.conectarBtn)
        
        self.statusLabel = QLabel('')
        self.statusLabel.setStyleSheet(TailwindStyle.get_label_style())
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

    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return super().default(obj)

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
                json.dump(dados, f, indent=2, ensure_ascii=False, cls=self.DateTimeEncoder)

class TestDataGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gerador de Dados de Teste')
        self.resize(800, 600)
        
        widget_central = QWidget()
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(16)
        layout_principal.setContentsMargins(24, 24, 24, 24)
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)
        
        titulo = QLabel('Gerador de Dados de Teste')
        titulo.setStyleSheet('font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 16px;')
        layout_principal.addWidget(titulo)
        
        btn_conexao = QPushButton('Configurar Conexão')
        btn_conexao.setStyleSheet(TailwindStyle.get_button_style())
        btn_conexao.clicked.connect(self.abrir_conexao)
        layout_principal.addWidget(btn_conexao)
        
        frame_tabela = QFrame()
        frame_tabela.setStyleSheet('background-color: #f3f4f6; border-radius: 8px; padding: 16px;')
        layout_tabela = QVBoxLayout()
        layout_tabela.setSpacing(8)
        
        label_tabela = QLabel('Selecione a Tabela:')
        label_tabela.setStyleSheet(TailwindStyle.get_label_style())
        layout_tabela.addWidget(label_tabela)
        
        self.combo_tabelas = QComboBox()
        self.combo_tabelas.setEnabled(False)
        self.combo_tabelas.setStyleSheet(TailwindStyle.get_input_style())
        layout_tabela.addWidget(self.combo_tabelas)
        
        frame_tabela.setLayout(layout_tabela)
        layout_principal.addWidget(frame_tabela)
        
        frame_quantidade = QFrame()
        frame_quantidade.setStyleSheet('background-color: #f3f4f6; border-radius: 8px; padding: 16px;')
        layout_quantidade = QHBoxLayout()
        layout_quantidade.setSpacing(8)
        
        label_quantidade = QLabel('Quantidade de Registros:')
        label_quantidade.setStyleSheet(TailwindStyle.get_label_style())
        layout_quantidade.addWidget(label_quantidade)
        
        self.input_quantidade = QLineEdit()
        self.input_quantidade.setText('10')
        self.input_quantidade.setStyleSheet(TailwindStyle.get_input_style())
        layout_quantidade.addWidget(self.input_quantidade)
        
        frame_quantidade.setLayout(layout_quantidade)
        layout_principal.addWidget(frame_quantidade)
        
        frame_formatos = QFrame()
        frame_formatos.setStyleSheet('background-color: #f3f4f6; border-radius: 8px; padding: 16px;')
        layout_formatos = QVBoxLayout()
        layout_formatos.setSpacing(8)
        
        label_formatos = QLabel('Formatos de Exportação:')
        label_formatos.setStyleSheet(TailwindStyle.get_label_style())
        layout_formatos.addWidget(label_formatos)
        
        grupo_exportacao = QHBoxLayout()
        grupo_exportacao.setSpacing(16)
        
        self.check_sql = QCheckBox('SQL')
        self.check_csv = QCheckBox('CSV')
        self.check_json = QCheckBox('JSON')
        
        for checkbox in [self.check_sql, self.check_csv, self.check_json]:
            checkbox.setStyleSheet(TailwindStyle.get_checkbox_style())
            grupo_exportacao.addWidget(checkbox)
        
        layout_formatos.addLayout(grupo_exportacao)
        frame_formatos.setLayout(layout_formatos)
        layout_principal.addWidget(frame_formatos)
        
        btn_gerar = QPushButton('Gerar Dados')
        btn_gerar.setStyleSheet(TailwindStyle.get_button_style())
        btn_gerar.clicked.connect(self.gerar_e_exportar)
        layout_principal.addWidget(btn_gerar)
        
        self.label_status = QLabel('')
        self.label_status.setStyleSheet(TailwindStyle.get_label_style())
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
    
    TailwindStyle.apply_style(app)
    
    gerador_gui = TestDataGeneratorGUI()
    gerador_gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()