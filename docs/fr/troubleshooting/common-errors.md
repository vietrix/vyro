# Dépannage

## `Invalid --app format`

Utilisez `<module>:<attribute>`, par exemple `examples.hello_world:app`.

## Erreurs de signature de route

Assurez-vous que les gestionnaires sont `async def` et que le premier argument est `ctx`.

## Problèmes de build natif

Installez la chaîne d'outils Rust et reconstruisez avec `maturin build --release`.

## Erreurs de compilation de Docs

Exécutez `mkdocs build --strict` et corrigez les liens rompus ou les pages manquantes.