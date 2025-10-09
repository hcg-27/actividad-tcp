# Actividad

Para esta actividad deberá programar una clase **SocketTCP** la cual 
implementará sockets orientados a conexión usando **Stop & Wait**. Esta clase
deberá funcionar de forma similar a los sockets orientados a conexión de
python. Además, usted deberá implementar un cliente y un servidor que usen
objetos tipo **SocketTCP** para comunicarse. Su clase **SocketTCP** deberá
utilizar sockets UDP para enviar la información, por lo que su tarea será
implementar **TCP** simplificado con Stop & Wait incluyendo **timeouts,
mensajes ACK**, etc. Su cliente debe ser capaz de enviar un archivo a la
dirección **(IP, Puerto)** donde se encuentre escuchando el servidor. Por
ejemplo, si queremos enviar el archivo **'archivo.txt'** a la dirección
**'(localhost, 8000)'**, veremos algo como:

    $ python3 cliente.py localhost 8000 < archivo.txt

Dado que los programas implementan comunicación confiable, se espera que el
archivo sea recibido por el programa receptor de manera íntegra.

**Para probar su implementación**, defina que el máximo tamaño de paquete (sin
incluir headers) es de 16 bytes, por lo tanto, cualquier comunicación que
supere esa cantidad de bytes debe ser dividida en múltiples paquetes. Se
sugiere cargar todo el archivo a memoria y usarlo como un arreglo de bytes para
dividirlo más fácilmente en paquetes. Recuerde que usted debe implementar
comunicación confiable junto a todo lo que necesite, como timeouts y mensajes
ACK

## Pasos a seguir

1. Cree un cliente y un servidor **provisorios** que se comuniquen con *sockets
   UDP*. El cliente debe leer un archivo cuya ubicación o ruta se recibe desde
   entrada estándar (usando la función **input** de python). Luego, el cliente
   debe enviar los contenidos desde el cliente e imprimir el contenido del
   archivo en salida estándar. Compruebe que el archivo se envió completamente,
   **si bien en este punto no se ha implementado comunicación confiable**, el
   envío de mensajes pequeños a localhost no debiese tener pérdida.

2. Ahora vamos a crear la clase **SocketTCP** (guarde la clase anterior en un
   tercer archivo *distinto* al cliente y el servidor). **El constructor** de
   esta clase deberá ser capaz de almacenar todos los recursos que va a
   necesitar para la comunicación (socket UDP, dirección de destino, dirección
   de origen, número de secuencia, **todo lo que usted considere necesario**).
   Su constructor no debe recibir parámetros, es decir, se invoca como:

    my_socket = SocketTCP()

3. Considerando headers **TCP** que contengan la información necesaria para
   usar Stop & Wait como se mostró en clases, añade a su clase dos funciones
   estáticas **parse_segment** que pueda pasar segmentos TCP a alguna
   estructura de datos más comoda y **create_segment** que pueda crear
   segmentos a partir de dicha estructura de datos. Para la estructura de sus
   headers TCP puede usar como guía el ejemplo provisto más abajo en la sección
   **Material e indicaciones para la actividad** o puede codificar su header
   usando bytes (use lo que le sea más cómodo considerando ventajas y
   desventajas).

4. Implemente *3-way handshake* para que el emisor le avise al receptor que va
   a comenzar el envío de mensjaes. Por ahora **no** se precupe de manejar
   pérdidas. **Para ello, añada a la clase socketTCP las siguientes
   funciones**:

    * **bind(address)**: se encarga de que el objeto **SocketTCP** escuche en
      la dirección **address**

    * **connect(address)**: Función que inicia la conexión desde un objeto
      **socketTCP** con otro que se encuentra escuchando en la dirección
      **address**. Dentro de esta función deberá implementar el lado del
      cliente del *3-way handshake*. Por simplicidad, haga que su número de
      secuencia inicial sea elegido aleatoriamente entre 0 y 100.

    * **accept()**: Función que se encuentra esperando una petición de SYN.
      Dentro de esta función deberá implementar el lado del servidor del *3-way
      handshake*. Si el handshake termina de forma exitosa, **esta función
      deberá retornar un nuevo** objeto del tipo **socketTCP junto a la
      dirección** donde se encuentra escuchando (bind) dicho objeto. La
      **dirección** del **nuevo socket** debe ser **distinta** a la del socket
      que llamó a **accept()**.  Cuide que su nuevo socket esté correctamente
      asociado a la nueva dirección y que recurede los números de secuencia,
      pues es este nuevo socket el que será utilizado posteriormente para
      enviar y recibir mensajes.

5. Implemente *Stop & Wait* usando un timeout fijo definido por ustedes. Para
ello, aproveché la función **settimeout** de los sockets no orientados a
conexión. **Note que estos timeouts levantan errores al cumplirse el tiempo
límite**. Su código debe **manejar** estos errores para saber cuándo debe
retransmitir un segmento (para ver cómo implementar un timeout vea **Materiales
e Indicaciones para la actividad**). **Para implementar Stop & Wait añada a la
clase socketTCP las siguientes funciones**:

    * **send(message)**: Esta función será la encargada de manejar *Stop &
      Wait* desde el lado del emisor tal como vimos en la versión simplificada
      en el video. Su función **send** deberá encargarse de dividir el mensaje
      **message** en trozos de tamaño máximo 16 bytes. Para ello, use como guía
      e código provisorio que implemento en el **paso 1**

    Para evitar que el receptor espere para siempre, **haga que el primer
    segmento enviado por la función send** le informe al receptor el **largo en
    bytes del mensaje message** que le va a enviar (**mesage_length =
    len(message)) y luego, a partir del segundo segmento, comience a enviar el
    mensaje. **Note** que **send** usa como número de secuencia inicial el
    último número de secuencia almacenado.

    * **recv(buff_size)**: Esta función será la encargada de manejar *Stop &
      Wait* desde el lado del receptor, tal como vimos en la versión
      simplificada mostrada en el video. El **primer segmento**  que reciba
      esta función contendrá el largo en bytes del mensaje que va a recibir
      desde el emisor **(message_length)**. Su función **recv** debe retornar
      una vez el largo de los **datos** recibidos (sin headers) sea igual a
      **min(message_length, buff_size)**.

    **Importante**: note que buff_size solo afecta el funcionamiento del
    socketTCP y no debería ser el mismo buffer del socket UDP utilizado
    internamente. El socket UDP debería tener un tamaño de buffer fijo

6. Implemente el *fin de conexión* para liberar recursos del emisor y receptor.
Para ello añada las funciones **close()** y **recv_close()** a la clase
**socketTCP**. La función **close()** debe implementar el cierre de conexión
desde el lado del "Host A" según lo visto en el video. La función
**recv_close() será la encargada de manejar el fín de conexión**, es decir,
esta se deberá encargar de continuar el cierre de conexión desde el lado del
"Host B" según lo visto en el video.

7. Modifique sus funciones de handshake (**connect** y **accept**) para que
puedan **manejar pérdidas** utilizando *Stop & Wait*. Note que existe un caso
borde en que se pierde el último ACK del handshake, **dibuje un diagrama de
este caso y adjúntelo a su informe**. A partir de este diagrama, determine una
solución. Es posible que para solucionar este caso borde deba modificar otras
funciones como **send** o **recv**.

8. Modifique su función de cierre para que tolere pérdidas. Para ello, haga las
siguientes modificaciones 

    * **close()**: Si su función **close()** no recibe los mensajes FIN y ACK
      esperados luego de un timeout, renueve el timeout y vuelva a enviar el
      mensaje FIN. haga que **close()** pueda esperar hasta 3 timeouts. Si al
      cumplirse el tercer tiemout no ha recibido los mensajes, simplemente
      asuma que la contraparte se cerró y cierre la conexión.

    En caso de recibir los mensajes FIN y ACK con éxito, reenvíe el último ACK
    tres veces. Espere un tiempo timeout entre cada envío.

    * **recv_close()**: Modifique su código para que, en caso de no recibir el
      último ACK de la secuencia de cierre, espere hasta 3 timeouts. Luego del
      tercer tiemout simplemente asuma que la contraparte se cerró y cierre la
      conexión

## Material e indicaciones para la actividad

### Ejemplo headers TCP

Para esta actividad debe definir una estructura para sus headers. Una forma de
definir sus headers (sin usar directamente bytes) es la siguiente

    [SYN]|||[ACK]|||[FIN]|||[SEQ]|||[DATOS]

Aquí los datos necesarios del *header* se encuentran definidos como strings
divididos por una secuencia "|||". Las variables [SYN],, [ACK] y [FIN]
corresponden a flags cuyo valor es 0 en caso de no estar siendo utilizadas, y
en 1 en caso de ser utilizadas. La variable [SEQ] corresponde al número de
secuencia. De esta forma, un mensaje SYN-ACK se podría ver como:

    SYN-ACK -> 1|||1|||0|||8|||

Mientras que una secuencia de datos con su respectivo ACK podría verse como:

    Datos -> 0|||0|||0|||98|||
    Mensaje de prueba ACK -> 0|||1|||0|||115|||
