# Pollenbase

## Website

Compile the typescript source files to their javascript equivalent:

Run

```bash
npx tsc
```
in the wwwroot directory

### Tailwindcss

See https://tailwindcss.com/docs/installation for installation.

To compile run
```bash
npx tailwindcss -i ./src/style.css -o ./css/pollenbase.css
```
in the wwwroot directory. You can add **--watch** to hot rebuild based on changes in the html and typescript files.
