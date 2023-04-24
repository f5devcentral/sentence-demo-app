const express = require('express')
const fs = require('fs')
const http = require('http')
const url = require('url');
const app = express()
const port = process.env.PORT || 8080

const files = fs.readdirSync('img')
for (let i = files.length - 1; i >= 0; i--) {
  if (files[i][0] === '.') files.splice(i, 1)
}

app.get('/', (req, res) => {
  console.log(`==== ${req.method} ${req.pathname}`);
  console.log('> Headers');
  console.log(req.headers);
  const path = `img/${files[Math.floor(Math.random() * files.length)]}`
  getImage(path, res)
})

app.get('/:id([1-9]|1[0-2])', (req, res) => {
  console.log(`==== ${req.method} ${req.pathname}`);
  console.log('> Headers');
  console.log(req.headers);
  const path = `img/${files[req.params.id - 1]}`
  getImage(path, res)
})

function getImage(path, res) {
  fs.readFile(path, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' })
      res.end(`Error handling: ${path}\n`)
    } else {
      res.writeHead(200, { 'Content-Type': 'image/jpeg' })
      res.end(data, 'binary')
      console.log("Serving " + path)
    }
  })
}

app.listen(port, () => {
  console.log('listening on port:', port)
})
