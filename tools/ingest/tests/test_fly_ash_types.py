"""Synthetic class-fidelity checks; no customer or research cohort data."""
from decimal import Decimal
import pytest
from open3dcp_ingest import convert
from open3dcp_ingest.cli import _write_outputs
from open3dcp_ingest.readers import read_flat_csv

@pytest.mark.parametrize('ash',[
 'Fly Ash Class C (kg/m3)','Fly Ash Class F (kg/m3)','Class C Fly Ash','Class F Fly Ash',
 'Fly Ash (Class C)','Fly Ash Type F','Fly Ash Grade unknown','Fly Ash C',
 'Fly Ash Class C (kg/m3),Fly Ash Class F (kg/m3)',
 'fly_ash_type_c','fly_ash_type_f_kg_m3','Fly-ash Class C','Fly  Ash Class F',
 'C Fly Ash','F Fly Ash','flyash C','FA (Class C)','F.A. (Class C)','PFA class F'])
@pytest.mark.parametrize('kind',['uci',None])
def test_uci_declared_type_cannot_collapse_or_overwrite(tmp_path,ash,kind):
 p=tmp_path/'uci.csv'
 p.write_text('Cement,'+ash+',Water,Age\n300,'+('20,30' if ',' in ash else '50')+',200,7\n')
 with pytest.raises(ValueError,match='fly-ash'):convert(str(p),kind=kind)

@pytest.mark.parametrize('header',['Fly Ash,Fly Ash','Cement,Cement'])
def test_duplicate_canonical_columns_refuse(tmp_path,header):
 p=tmp_path/'uci.csv';p.write_text(header+',Water\n20,30,200\n')
 with pytest.raises(ValueError,match='same component'):convert(str(p),kind='uci')

@pytest.mark.parametrize('cls,key',[('C','fly_ash_type_c'),('F','fly_ash_type_f'),('','fly_ash')])
def test_flat_preserves_class_and_generic_unknown(tmp_path,cls,key):
 p=tmp_path/'flat.csv';p.write_text('cement_kg_m3,fly_ash_kg_m3,water_kg_m3,fine_agg_kg_m3,fly_ash_class\n300,50,200,450,'+cls+'\n')
 result,_=convert(str(p),kind='flat')
 assert result.rows[0][key]==5.
 assert all(not result.rows[0].get(k) for k in {'fly_ash','fly_ash_type_c','fly_ash_type_f'}-{key})

def test_canonical_keeps_c_f_both_and_generic_separate(tmp_path):
 p=tmp_path/'canonical.csv';p.write_text('mix_id,fly_ash,fly_ash_type_c,fly_ash_type_f\nC,,5,\nF,,,5\nBoth,1,2,3\nUnknown,5,,\n')
 result,report=convert(str(p),kind='canonical')
 assert [[r[k] for k in ('fly_ash','fly_ash_type_c','fly_ash_type_f')] for r in result.rows]==[
  [None,Decimal(5),None],[None,None,Decimal(5)],[Decimal(1),Decimal(2),Decimal(3)],[Decimal(5),None,None]]
 export,*_=_write_outputs(result,report,str(p),str(tmp_path/'export'))
 second,_=convert(export,kind='canonical');assert second.rows==result.rows

def test_unknown_flat_typed_headers_retained_and_mass_balance_held(tmp_path):
 p=tmp_path/'flat.csv';p.write_text('cement_kg_m3,fly_ash_type_c_kg_m3,fly_ash_type_f_kg_m3,water_kg_m3,fine_agg_kg_m3\n300,20,30,200,450\n')
 assert read_flat_csv(str(p))[0]['_ctx']['total_wet_mass_is_complete'] is False
 result,_=convert(str(p),kind='flat')
 assert {'source.fly_ash_type_c_kg_m3','source.fly_ash_type_f_kg_m3'}<={u.source for u in result.unmapped}
 assert not result.rows[0].get('fly_ash')


@pytest.mark.parametrize('header',['fly_ash_type_c','fly_ash_type_f_kg_m3','Fly-ash Class C','Fly  Ash Class F',
 'C Fly Ash','F Fly Ash','flyash C','FA (Class C)','F.A. (Class C)'])
def test_original_yeh_plus_typed_extra_still_refuses(tmp_path,header):
 p=tmp_path/'uci.csv'
 p.write_text('Cement,Blast Furnace Slag,Fly Ash,Water,Superplasticizer,Coarse Aggregate,Fine Aggregate,Age,'+header+'\n300,0,0,200,0,0,450,7,50\n')
 for kind in ('uci',None):
  with pytest.raises(ValueError,match='fly-ash'):convert(str(p),kind=kind)

@pytest.mark.parametrize('header',['extra powder kg/m3','unknown_additive_kg_m3','extra mass','extra_weight_g','extra dose ml/m3'])
def test_unknown_mass_cannot_claim_complete_yeh_denominator(tmp_path,header):
 p=tmp_path/'uci.csv'
 p.write_text('Cement,Blast Furnace Slag,Fly Ash,Water,Superplasticizer,Coarse Aggregate,Fine Aggregate,Age,'+header+'\n300,0,0,200,0,0,450,7,50\n')
 from open3dcp_ingest.readers import read_uci_csv
 assert read_uci_csv(str(p))[0]['_ctx']['total_wet_mass_is_complete'] is False
 result,_=convert(str(p),kind='uci')
 assert any(u.source=='source.'+header and u.value=='50' for u in result.unmapped)
 assert all(t.fidelity!='exact' for t in result.trace if t.target in ('water','cement_unspecified'))


def test_metadata_extra_is_preserved_without_becoming_ingredient_mass(tmp_path):
 p=tmp_path/'uci.csv'
 p.write_text('Cement,Blast Furnace Slag,Fly Ash,Water,Superplasticizer,Coarse Aggregate,Fine Aggregate,Age,source_row_id\n300,0,50,200,0,0,450,7,123\n')
 from open3dcp_ingest.readers import read_uci_csv
 assert read_uci_csv(str(p))[0]['_ctx']['total_wet_mass_is_complete'] is True
 result,_=convert(str(p),kind='uci')
 assert any(u.source=='source.source_row_id' and u.value=='123' for u in result.unmapped)
