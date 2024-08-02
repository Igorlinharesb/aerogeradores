# src/dados_geograficos.py

import requests
import os
import geopandas as gpd
from shapely.geometry import Point
from typing import Dict, Union

def get_raw_data(params: Dict[str, Union[str, int]]) -> Dict:
    """
    Faz uma requisição GET para a URL fornecida com os parâmetros dados e retorna os dados em formato JSON.

    Args:
        params (Dict[str, Union[str, int]]): Parâmetros da query a serem enviados na requisição.

    Returns:
        Dict: Dados em formato JSON se a requisição for bem-sucedida, caso contrário, um dicionário vazio.
    """
    url = "https://sigel.aneel.gov.br/arcgis/rest/services/PORTAL/WFS/MapServer/0/query"
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na requisição: {response.status_code}")
        return {}
    

def get_geodataframe(data: Dict) -> gpd.GeoDataFrame:
    """
    Converte os dados em formato JSON para um GeoDataFrame do GeoPandas.

    Args:
        data (Dict): Dados em formato JSON com as características e geometrias.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame contendo as propriedades e geometrias transformadas.
    """
    features = data.get('features', [])
    properties = [feature.get('attributes', {}) for feature in features]
    geometry = [Point(feature.get('geometry', {}).get('x', 0), feature.get('geometry', {}).get('y', 0)) for feature in features]
    
    # Criando o GeoDataFrame com a projeção UTM 23S (WGS84 / UTM zone 23S)
    gdf = gpd.GeoDataFrame(properties, geometry=geometry, crs="EPSG:32723")
    
    # Extraindo latitude e longitude
    gdf['latitude'] = gdf.geometry.y
    gdf['longitude'] = gdf.geometry.x
    
    return gdf

def save_csv_file(gdf: gpd.GeoDataFrame, file_name: str = 'dados_geograficos', output_dir: str = 'outputs') -> None:
    """
    Salva o GeoDataFrame como um arquivo CSV no diretório especificado.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame a ser salvo.
        file_name (str, optional): Nome do arquivo CSV a ser criado. Default é 'dados_geograficos'.
        output_dir (str, optional): Diretório onde o arquivo CSV será salvo. Default é 'outputs'.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    csv_path = os.path.join(output_dir, f"{file_name}.csv")
    gdf.to_csv(csv_path, index=False)
    print(f"Arquivo CSV salvo em: {csv_path}")
